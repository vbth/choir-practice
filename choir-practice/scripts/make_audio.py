#!/usr/bin/env python3
"""Create all practice audio (MP3) and MIDI files – always in two sound versions: choir ("Choir Aahs")
and optimised piano (legato). Input: final MusicXML (one voice per staff) and score.json
(voices, seating, melody voice, tempo, language).

  python3 make_audio.py final.musicxml score.json outdir --slug Title [--workdir WORK]

Output (names from the language pack; <S> = choir|piano sound name, <stage> = solo|accomp|choir stage name):
  <practice>/<S>/<stage>/{MP3,MIDI}/<slug>_<stage>_<Voice>_<S>.*        normal tempo
  <practice>/<S>/<stage>/<slow>/{MP3,MIDI}/..._<slow>.*                  solo + accomp only, SLOW_PCT % tempo
  <tutti>/<S>/<slug>_Tutti_<S>.{mp3,mid}
  outdir/mixes.json   levels/positions/settings (for overview PDF, README, verify)

Stages:  solo   – own voice only
         accomp – own voice, melody voice LV['melody'] dB, piano accompaniment of all voices LV['accomp'] dB
                  (melody singers: own voice + accompaniment). Accompaniment is piano in both sound versions.
         choir  – choir seating: neighbours ±0.6 at LV['near'], edge voices get the next-but-one voice on the
                  free side at LV['second'], all others far out at LV['far']. Both ears always filled.
Each voice file starts with the own starting note ("starting pitch"), a pause, then the music directly.
Tutti files start with every voice's starting note one after another (low to high), a pause, then the music.
A bar of count-in clicks is optional (COUNT_IN = True, off by default).
Sound chain: FluidSynth + MuseScore General (Full; fallback FluidR3_GM) – every voice rendered as a mono
stem and mixed with ffmpeg (MIDI pan is too weak with stereo soundfonts), light room reverb via a
synthetic impulse response, legato articulation, loudness LUFS, MP3 192 kbit/s.
"""
import os, sys, json, math, argparse, subprocess, tempfile, shutil
import mido
from lxml import etree
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import load_i18n, safe, log_check, derive_playback

SF_CANDIDATES = ['/usr/share/sounds/sf3/MuseScore_General_Full.sf3', '/usr/share/sounds/sf3/MuseScore_General.sf3',
                 '/usr/share/sounds/sf2/FluidR3_GM.sf2']
SF = next((p for p in SF_CANDIDATES if os.path.exists(p)), SF_CANDIDATES[-1])
LV = {'near': -7, 'second': -9, 'far': -12, 'melody': -4, 'accomp': -12, 'tutti': -3}   # dB relative to own voice
REVERB = {'on': True, 'rt': 1.3, 'wet': 0.30}
LUFS = -19
SLOW_PCT = 75
PROG = {'choir': 52, 'piano': 0}            # GM program, 0-based
TPQ = 480
VEL = {'ppp': 35, 'pp': 45, 'p': 58, 'mp': 70, 'mf': 82, 'f': 96, 'ff': 110, 'fff': 120}
STEP = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
BEATQ = {'quarter': 1, 'dotted-quarter': 1.5, 'half': 2, 'dotted-half': 3, 'eighth': 0.5, 'whole': 4}
# starting pitch: single notes one after another (voice files: only the own note; tutti: every voice's note, low to high),
# then a pause before the music (gap_s)
INTRO = {'note_s': 2.0, 'note_gap_s': 0.8, 'gap_s': 3.0, 'verse_gap_s': 2.0}   # starting note 2.0 s, 0.8 s between the voices' notes (tutti), 3.0 s pause before the music
COUNT_IN = False   # one bar of count-in clicks before the entry; off by default (adds nothing for singers), set True to bring it back
# trim silence only at the END (reverse → trim start → reverse); a plain silenceremove with stop_periods=-1
# also shortened quiet passages inside the file (intro pause, rests) and broke the timing
POST = f'areverse,silenceremove=start_periods=1:start_threshold=-60dB:start_silence=0.8,areverse,loudnorm=I={LUFS}:TP=-2'
IR = None

# ---------- score reading --------------------------------------------------------------------------
def playback_order(spec):
    """Measure ranges in played order (see common.derive_playback): spec['playback'] or derived from spec['repeats']."""
    return derive_playback(spec or {})

def read_score(xml, order=None, tempo_q=None):
    r = etree.parse(xml).getroot()
    div = int(r.find('.//divisions').text)
    tm = r.find('.//time'); beats, bt = int(tm.findtext('beats')), int(tm.findtext('beat-type'))
    parts = []
    for p in r.findall('part'):
        ev, ctrl, fermata_ends = [], [], []; pos = 0; cpos = 0   # cpos: start of the last non-chord note (chord notes share it)
        ms = p.findall('measure')
        gaps = set()   # indices in ms where a new verse starts (the piece restarts at measure 1): a pause is inserted there
        if order:
            ms2 = []
            for n, (a, b) in enumerate(order):
                if n and a == 1: gaps.add(len(ms2))
                ms2 += [ms[i - 1] for i in range(a, b + 1)]
            ms = ms2
        gap_div = int(INTRO['verse_gap_s'] * tempo_q / 60 * div) if tempo_q else 0
        for mi, m in enumerate(ms):
            if mi in gaps: pos += gap_div; cpos = pos
            for e in m:
                if e.tag == 'direction':
                    for dt in e.findall('direction-type'):
                        if dt.find('dynamics') is not None: ctrl.append((pos, 'dyn', dt.find('dynamics')[0].tag))
                        if dt.find('wedge') is not None: ctrl.append((pos, 'wedge', dt.find('wedge').get('type')))
                        w = (dt.findtext('words') or '').strip().lower()
                        if w.startswith(('dim', 'decresc')): ctrl.append((pos, 'wedge', 'diminuendo'))
                        if w.startswith('cresc'): ctrl.append((pos, 'wedge', 'crescendo'))
                    continue
                if e.tag in ('backup', 'forward'):
                    d = int(e.findtext('duration')); pos += -d if e.tag == 'backup' else d; continue
                if e.tag != 'note': continue
                d = int(e.findtext('duration')); is_chord = e.find('chord') is not None
                at = cpos if is_chord else pos   # chord notes (divisi in one staff) start with the previous note
                if not is_chord: cpos = pos
                if e.find('rest') is None and e.find('pitch') is not None:
                    pt = e.find('pitch')
                    key = 12 * (int(pt.findtext('octave')) + 1) + STEP[pt.findtext('step')] + int(float(pt.findtext('alter') or 0))
                    stop = any(x.get('type') == 'stop' for x in e.findall('tie'))
                    prev = next((x for x in reversed(ev) if x[2] == key and x[0] + x[1] == at), None) if stop else None
                    if prev: prev[1] += d
                    else: ev.append([at, d, key, 0])
                    if e.find('notations/fermata') is not None: fermata_ends.append(at + d)
                if not is_chord: pos += d
        parts.append({'id': p.get('id'), 'events': ev, 'ctrl': sorted(ctrl, key=lambda x: x[0]), 'fermatas': fermata_ends, 'total': pos})
    names = {sp.get('id'): sp.findtext('part-name') for sp in r.iter('score-part')}
    for pt in parts: pt['label'] = names.get(pt['id'], pt['id'])
    first = r.find('part/measure')
    pickup = sum(int(n.findtext('duration')) for n in first.findall('note') if n.find('chord') is None) if first.get('implicit') == 'yes' else 0
    return {'div': div, 'beats': beats, 'bt': bt, 'parts': parts, 'pickup': pickup}

def velocities(part):
    """Dynamics: steps from dynamic marks; hairpins / 'dim.' / 'cresc.' ramp linearly to the next dynamic
    after the hairpin end (none: ±14 velocity)."""
    ctrl = part['ctrl']; dyns = [(t, VEL.get(v, VEL['mf'])) for t, k, v in ctrl if k == 'dyn']
    wedges, opened = [], None
    for t, k, v in ctrl:
        if k == 'wedge' and v in ('crescendo', 'diminuendo'): opened = (t, v)
        elif k == 'wedge' and v == 'stop' and opened: wedges.append((opened[0], t, opened[1])); opened = None
    if opened: wedges.append((opened[0], part['total'], opened[1]))
    def step(t):
        v = dyns[0][1] if dyns else VEL['mf']
        for dt, dv in dyns:
            if dt <= t: v = dv
        return v
    ramps = []
    for t0, t1, kind in wedges:
        v0 = step(t0); nxt = [dv for dt, dv in dyns if dt >= t1 and dt > t0]
        ramps.append((t0, t1, v0, nxt[0] if nxt else max(35, min(120, v0 + (14 if kind == 'crescendo' else -14)))))
    def vel_at(t):
        for t0, t1, v0, v1 in ramps:
            if t0 <= t < t1: return round(v0 + (v1 - v0) * (t - t0) / max(1, t1 - t0))
        last = None
        for t0, t1, v0, v1 in ramps:
            if t1 <= t and not any(t1 <= dt <= t for dt, _ in dyns): last = v1
        return last if last is not None else step(t)
    for e in part['events']: e[3] = vel_at(e[0])

def apply_fermatas(score):
    ends = sorted({t for p in score['parts'] for t in p['fermatas']}); total = max(p['total'] for p in score['parts'])
    shifts = []
    for t in ends:
        if t >= total:
            for p in score['parts']:
                for e in p['events']:
                    if e[0] + e[1] == t: e[1] = int(e[1] * 1.6)
        else:
            dur = max((e[1] for p in score['parts'] for e in p['events'] if e[0] + e[1] == t), default=score['div'])
            shifts.append((t, int(dur * 0.6)))
    for t, s in sorted(shifts, reverse=True):
        for p in score['parts']:
            for e in p['events']:
                if e[0] >= t: e[0] += s
                elif e[0] + e[1] == t: e[1] += s

def to_ticks(score):
    """Convert to MIDI ticks and apply legato: repeated pitch ends 15 ticks early, pitch change overlaps 10 ticks."""
    f = TPQ / score['div']
    for p in score['parts']:
        p['tev'] = ev = [[int(e[0] * f), int(e[1] * f), e[2], e[3]] for e in p['events']]
        starts = {}
        for e in ev: starts.setdefault(e[0], []).append(e[2])
        for e in ev:   # note(s) starting where this one ends: same pitch → gap, other pitch → overlap
            nxt = starts.get(e[0] + e[1])
            if nxt: e[1] += (-15 if e[2] in nxt else 10)

def countin(score):
    if not COUNT_IN: return [], 0   # no clicks, music starts right after the intro pause
    div = score['div']; beats, bt = score['beats'], score['bt']; bar = int(beats * div * 4 / bt)
    n, blen = (beats // 3, 3 * div // 2) if (bt == 8 and beats % 3 == 0 and beats > 3) else (beats, int(div * 4 / bt))
    f = TPQ / div
    return [int(k * blen * f) for k in range(n)], int((bar - score['pickup']) * f) if score['pickup'] else int(bar * f)

def sec2ticks(s, tempo_q):
    return int(s * tempo_q / 60 * TPQ)

# ---------- MIDI ------------------------------------------------------------------------------------
def write_midi(path, score, tracks, tempo_q, clicks, start, intro=None):
    """tracks: (part index, cc7, cc10, program). intro: (keys, program) – the starting notes, played one after another
    (INTRO note_s each, note_gap_s between), then a pause gap_s, before the music (and the optional count-in)."""
    shift = 0
    mf = mido.MidiFile(ticks_per_beat=TPQ, type=1); t0 = mido.MidiTrack(); mf.tracks.append(t0)
    t0 += [mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(tempo_q), time=0),
           mido.MetaMessage('time_signature', numerator=score['beats'], denominator=score['bt'], time=0)]
    msgs0 = []
    if intro:
        keys, prog_ = intro
        n_len = sec2ticks(INTRO['note_s'], tempo_q); g_len = sec2ticks(INTRO['note_gap_s'], tempo_q); t = 0
        msgs0 += [(0, 1, mido.Message('program_change', channel=14, program=prog_))]
        for k in keys:
            msgs0 += [(t, 2, mido.Message('note_on', channel=14, note=k, velocity=85)), (t + n_len, 0, mido.Message('note_off', channel=14, note=k, velocity=0))]
            t += n_len + g_len
        shift = (t - g_len if keys else 0) + sec2ticks(INTRO['gap_s'], tempo_q)
    for k, c in enumerate(clicks):
        nt = 76 if k == 0 else 77
        msgs0 += [(shift + c, 2, mido.Message('note_on', channel=9, note=nt, velocity=90)), (shift + c + 60, 0, mido.Message('note_off', channel=9, note=nt, velocity=0))]
    msgs0.sort(key=lambda x: (x[0], x[1])); now = 0
    for t, _, m in msgs0: t0.append(m.copy(time=t - now)); now = t
    for ch, (i, cc7, cc10, prg) in enumerate(tracks):
        chn = ch if ch < 9 else ch + 1
        p = score['parts'][i]; tr = mido.MidiTrack(); mf.tracks.append(tr)
        tr += [mido.MetaMessage('track_name', name=p['label'], time=0), mido.Message('program_change', channel=chn, program=prg, time=0),
               mido.Message('control_change', channel=chn, control=7, value=cc7, time=0), mido.Message('control_change', channel=chn, control=10, value=cc10, time=0)]
        msgs = []
        for s, d, key, v in p['tev']:
            s += start + shift
            msgs += [(s, 1, mido.Message('note_on', channel=chn, note=key, velocity=v)), (s + d, 0, mido.Message('note_off', channel=chn, note=key, velocity=0))]
        msgs.sort(key=lambda x: (x[0], x[1])); now = 0
        for t, _, m in msgs: tr.append(m.copy(time=t - now)); now = t
    mf.save(path)
    return shift

# ---------- audio -----------------------------------------------------------------------------------
def render(mid, wav, mono=False):
    tmp = wav + '.st.wav' if mono else wav
    subprocess.run(['fluidsynth', '-ni', '-r', '44100', '-F', tmp, SF, mid], check=True, capture_output=True)
    if mono:
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', tmp, '-af', 'pan=mono|c0=0.5*c0+0.5*c1', wav], check=True); os.remove(tmp)

def make_ir(path, rt=1.3, sr=44100):
    """Synthetic stereo impulse response (decaying, slightly smoothed noise) for a discreet room reverb."""
    import numpy as np, wave
    n = int(sr * rt * 1.2); t = np.arange(n) / sr; rng = np.random.default_rng(7)
    env = np.exp(-6.9 * t / rt); pre = int(0.018 * sr); out = np.zeros((n + pre, 2))
    for c in range(2): out[pre:, c] = np.convolve(rng.standard_normal(n) * env, np.ones(6) / 6, mode='same')
    out = out / np.abs(out).max() * 0.5
    with wave.open(path, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes((out * 32767).astype('<i2').tobytes())
    return path

def lr(p, db):
    g = 10 ** (db / 20); a = (p + 1) * math.pi / 4
    return g * math.cos(a) * math.sqrt(2), g * math.sin(a) * math.sqrt(2)

def mix(inputs_db, mp3):
    """inputs_db: list of (wav, pan -1..1, dB[, delay in s]). Constant-power pan, sum, reverb, loudness, MP3."""
    inputs, parts, labels = [], [], []
    for j, item in enumerate(inputs_db):
        wav, p, db = item[:3]; ms = round(item[3] * 1000) if len(item) > 3 else 0
        inputs += ['-i', wav]; L, R = lr(p, db)
        parts.append(f'[{j}:a]pan=stereo|c0={L:.4f}*c0|c1={R:.4f}*c0' + (f',adelay={ms}|{ms}' if ms > 0 else '') + f'[s{j}]'); labels.append(f'[s{j}]')
    fc = ';'.join(parts) + ';' + ''.join(labels) + f'amix=inputs={len(labels)}:normalize=0:duration=longest[m]'
    if REVERB['on']:
        inputs += ['-i', IR]; k = len(inputs_db)
        fc += (f';[m]asplit=2[dry][w0];[w0][{k}:a]afir=dry=0:wet=1:length=1[w1];'
               f'[dry][w1]amix=inputs=2:weights=1 {REVERB["wet"]}:normalize=0[rv];[rv]{POST}[o]')
    else:
        fc += f';[m]{POST}[o]'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error'] + inputs + ['-filter_complex', fc, '-map', '[o]', '-ar', '44100', '-b:a', '192k', mp3], check=True)

def stages(seat, melody):
    """Level/position tables. seat: voice ids left->right. Entries (voice, pan, dB, source 'own'|'acc')."""
    N = len(seat); out = {'solo': {}, 'accomp': {}, 'choir': {}}
    spread = {v: (-0.5 + 1.0 * k / (N - 1)) if N > 1 else 0 for k, v in enumerate(seat)}
    for i, own in enumerate(seat):
        out['solo'][own] = [(own, 0.0, 0, 'own')]
        st = [(own, 0.0, 0, 'own')]
        if melody and melody != own and melody in seat:
            st.append((melody, 0.45 if seat.index(melody) > i else -0.45, LV['melody'], 'own'))
        st += [(v, round(spread[v], 2), LV['accomp'], 'acc') for v in seat]
        out['accomp'][own] = st
        b = [(own, 0.0, 0, 'own')]
        others = [(v, k - i) for k, v in enumerate(seat) if v != own]
        edge = bool(others) and (all(r > 0 for _, r in others) or all(r < 0 for _, r in others))
        flipped = next((v for v, r in others if abs(r) == 2), None) if edge else None
        far = sorted([(v, r) for v, r in others if abs(r) >= 2 and v != flipped], key=lambda x: abs(x[1]))
        for v, r in others:
            sgn = 1 if r > 0 else -1
            if abs(r) == 1: b.append((v, 0.6 * sgn, LV['near'], 'own'))
            elif v == flipped: b.append((v, -0.6 * sgn, LV['second'], 'own'))
            else:
                k3 = far.index((v, r)); b.append((v, round(sgn * min(0.95, 0.8 + 0.15 * (k3 + 1) / max(1, len(far))), 2), LV['far'], 'own'))
        out['choir'][own] = b
    return out

def main():
    global SF, IR, SLOW_PCT
    ap = argparse.ArgumentParser(); ap.add_argument('xml'); ap.add_argument('spec'); ap.add_argument('outdir')
    ap.add_argument('--slug', required=True); ap.add_argument('--workdir'); ap.add_argument('--no-reverb', action='store_true')
    ap.add_argument('--slow-pct', type=int, default=SLOW_PCT, help='tempo of the slow versions in %% of the normal tempo (10 to 95, default %(default)s)')
    ap.add_argument('--soundfont'); ap.add_argument('--only', help='trial run: stage:voice, e.g. accomp:B2 (no tutti, normal tempo)')
    A = ap.parse_args()
    if A.no_reverb: REVERB['on'] = False
    if not 10 <= A.slow_pct <= 95: sys.exit('--slow-pct must be between 10 and 95')
    SLOW_PCT = A.slow_pct
    if A.soundfont: SF = A.soundfont
    spec = json.load(open(A.spec, encoding='utf-8')); i18 = load_i18n(spec.get('language', 'en'))
    vids = [v['id'] for v in spec['voices']]; vname = {v['id']: v['name'] for v in spec['voices']}
    seat = spec.get('seating') or vids; melody = spec.get('melody'); idx = {v: k for k, v in enumerate(vids)}
    tempo = spec.get('tempo', {}); bpm = tempo.get('bpm'); beat = tempo.get('beat') or 'quarter'
    if not bpm: sys.exit('tempo.bpm missing in score.json – decide it (references/musical-defaults.md) and get it approved')
    score = read_score(A.xml, playback_order(spec), bpm * BEATQ[beat])
    for p in score['parts']: velocities(p)
    apply_fermatas(score); to_ticks(score)
    clicks, start = countin(score)
    # starting note = the voice's EARLIEST note in time (events are stored in document order, which is not always time order)
    first = {v: (min(score['parts'][idx[v]]['tev'], key=lambda e: e[0])[2] if score['parts'][idx[v]]['tev'] else None) for v in vids}
    own_keys = lambda v: [first[v]] if first[v] else []        # voice files: only the own starting note
    tutti_keys = sorted({k for k in first.values() if k})       # tutti: every voice's starting note, low to high
    # the tutti intro is longer than the voice-file intro; the (shared) voice stems are delayed by the difference
    tutti_delay = max(0, len(tutti_keys) - 1) * (INTRO['note_s'] + INTRO['note_gap_s'])
    V = stages(seat, melody)
    work = tempfile.mkdtemp(prefix='audio_'); IR = make_ir(os.path.join(work, 'ir.wav'), REVERB['rt'])
    S = safe(A.slug); out = A.outdir; fold = i18['folders']; snd = i18['sounds']; stg = i18['stages']
    tempos = {'normal': bpm * BEATQ[beat]}
    if not A.only: tempos['slow'] = bpm * BEATQ[beat] * SLOW_PCT / 100
    made = 0
    for tname, tq in tempos.items():
        # mono stems per sound (with intro shift so that all stems line up), click and intro stems
        stems = {}
        for sk, prog in PROG.items():
            for v in vids:
                m = os.path.join(work, f'{tname}_{sk}_{v}.mid')
                write_midi(m, score, [(idx[v], 127, 64, prog)], tq, [], start, intro=(own_keys(v), prog))
                # remove intro notes from the voice stem (intro is rendered separately)
                mm = mido.MidiFile(m)
                for tr in mm.tracks:
                    for j, msg in enumerate(tr):
                        if msg.type in ('note_on', 'note_off') and msg.channel in (14, 15): tr[j] = msg.copy(velocity=0)
                mm.save(m)
                w = os.path.join(work, f'{tname}_{sk}_{v}.wav'); render(m, w, mono=True); stems[(sk, v)] = w
        # the click stem must use the SAME intro length as the voice stems (one starting note + gap), otherwise
        # the count-in starts too early; the intro notes themselves are muted below
        click_in = []   # click stem only when COUNT_IN is on (an empty MIDI would render a useless silent stem)
        if clicks:
            cm = os.path.join(work, f'{tname}_click.mid'); write_midi(cm, score, [], tq, clicks, start, intro=([tutti_keys[0] if tutti_keys else 60], 0))
            mm = mido.MidiFile(cm)
            for tr in mm.tracks:
                for j, msg in enumerate(tr):
                    if msg.type in ('note_on', 'note_off') and msg.channel in (14, 15): tr[j] = msg.copy(velocity=0)
            mm.save(cm); click = os.path.join(work, f'{tname}_click.wav'); render(cm, click, mono=True)
            click_in = [(click, 0.0, -6)]
        intro_w = {}
        for sk, prog in PROG.items():
            for v in vids + [None]:
                im_ = os.path.join(work, f'{tname}_intro_{sk}_{v}.mid')
                write_midi(im_, score, [], tq, [], start, intro=(own_keys(v) if v else tutti_keys, prog))
                w = os.path.join(work, f'{tname}_intro_{sk}_{v}.wav'); render(im_, w, mono=True); intro_w[(sk, v)] = w
        for sk, prog in PROG.items():
            for stage, table in V.items():
                if tname == 'slow' and stage == 'choir': continue
                for own in vids:
                    if A.only and A.only != f'{stage}:{own}': continue
                    lay = table[own]
                    d = os.path.join(out, fold['practice'], snd[sk], stg[stage])
                    if tname == 'slow': d = os.path.join(d, i18['slow'])
                    os.makedirs(d + '/MP3', exist_ok=True); os.makedirs(d + '/MIDI', exist_ok=True)
                    base = f'{S}_{stg[stage]}_{safe(vname[own])}_{snd[sk]}' + (f'_{i18["slow"]}' if tname == 'slow' else '')
                    src = [(stems[('piano' if (s == 'acc' or sk == 'piano') else 'choir', v)], p, db) for v, p, db, s in lay]
                    mix(click_in + [(intro_w[(sk, own)], 0.0, -3)] + src, f'{d}/MP3/{base}.mp3')
                    write_midi(f'{d}/MIDI/{base}.mid', score,
                               [(idx[v], round(127 * 10 ** (db / 40)), max(0, min(127, round(64 + p * 63))), 0 if s == 'acc' else prog) for v, p, db, s in lay],
                               tq, clicks, start, intro=(own_keys(own), prog))
                    made += 2
            if tname == 'normal' and not A.only:
                d = os.path.join(out, fold['tutti'], snd[sk]); os.makedirs(d, exist_ok=True)
                spread = {v: (-0.6 + 1.2 * k / (len(seat) - 1)) if len(seat) > 1 else 0 for k, v in enumerate(seat)}
                base = f'{S}_{i18["files"]["tutti"]}_{snd[sk]}'
                write_midi(f'{d}/{base}.mid', score, [(idx[v], 100, round(64 + spread[v] * 63), prog) for v in vids], tq, clicks, start, intro=(tutti_keys, prog))
                mix([(c_[0], c_[1], c_[2], tutti_delay) for c_ in click_in] + [(intro_w[(sk, None)], 0.0, -3)]
                    + [(stems[(sk, v)], spread[v], LV['tutti'], tutti_delay) for v in vids], f'{d}/{base}.mp3')
                made += 2
        print(tname, 'done')
    json.dump({'seating': seat, 'melody': melody, 'names': vname,
               'stages': {k: {o: [list(x) for x in lay] for o, lay in t.items()} for k, t in V.items()},
               'tempo': {'bpm': bpm, 'beat': beat, 'text': tempo.get('text'), 'slow_pct': SLOW_PCT},
               'levels': LV, 'lufs': LUFS, 'soundfont': os.path.basename(SF), 'reverb': REVERB,
               'intro': INTRO, 'files': made}, open(os.path.join(out, 'mixes.json'), 'w'), ensure_ascii=False, indent=1)
    shutil.rmtree(work, ignore_errors=True)
    print(f'{made} files | tempo {bpm} {beat} (slow {SLOW_PCT} %) | soundfont {os.path.basename(SF)} | {LUFS} LUFS')
    if A.workdir: log_check(A.workdir, 5, 'make_audio', 'pass', f'{made} audio/MIDI files, soundfont {os.path.basename(SF)}, {LUFS} LUFS')

if __name__ == '__main__':
    main()
