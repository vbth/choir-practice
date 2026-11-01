#!/usr/bin/env python3
"""Final gate: check the finished package folder before zipping. Exit code 1 if anything fails.

  python3 verify.py PKG score.json --workdir WORK

Checks
  structure   score PDF, MusicXML choir/piano, overview PDF,
              every voice × sound × stage MP3+MIDI (+ slow for solo/accomp), tutti, README.md/.pdf,
              check log and correction log (.md/.pdf), session_handoff.md
  score       A4 portrait pages; layout.json: scale ≥ min, fill ≥ 0.8, not compressed
  overview    exactly 1 page, A4 landscape
  lyrics      per verse the same text in all voices (voices with overrides: same words, order kept)
  midi        every MIDI file against the final MusicXML: tempo, starting notes, onset + pitch of every note per voice,
              notes lost (e.g. chord notes). Finds errors of the audio step, not transcription errors (same source).
  audio       MP3 durations consistent per stage and tempo (±15 % of the median), no file under 5 s
  names       file and folder names are ASCII-safe (no umlauts/spaces)
"""
import os, sys, json, glob, re, argparse, subprocess, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import load_i18n, safe, log_check
from pypdf import PdfReader
from lxml import etree

def dur(f):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f], capture_output=True, text=True)
    try: return float(r.stdout.strip())
    except ValueError: return 0.0

def check_midi(pkg, spec, i18, xml, fails, warns):
    """Compare every MIDI file with the final MusicXML: tempo, starting notes, and for every sounding voice the
    onset and pitch of every note (fermatas and intro shift worked in). Returns the number of files compared, or
    None if the check could not run. This catches errors of the audio step (wrong starting note, lost or shifted
    notes); it cannot catch a transcription error, because the MIDI is made from the same MusicXML."""
    try:
        import mido, make_audio as MA
    except ImportError as e:
        warns.append(f'MIDI check skipped ({e}) – run setup.sh'); return None
    fo, snd, stg = i18['folders'], i18['sounds'], i18['stages']; slug = safe(spec['meta']['title'])
    mpath = next((p for p in (os.path.join(pkg, 'mixes.json'), os.path.join(pkg, fo['tools'], 'mixes.json')) if os.path.exists(p)), None)
    if not mpath or not os.path.exists(xml):
        warns.append('MIDI check skipped (mixes.json or MusicXML not found)'); return None
    mixes = json.load(open(mpath, encoding='utf-8'))
    _t = mixes['tempo']; score = MA.read_score(xml, MA.playback_order(spec), _t['bpm'] * MA.BEATQ[_t.get('beat') or 'quarter']); MA.apply_fermatas(score); MA.to_ticks(score)
    clicks, start = MA.countin(score)
    vids = [v['id'] for v in spec['voices']]; idx = {v: k for k, v in enumerate(vids)}
    first = {v: (min(score['parts'][idx[v]]['tev'], key=lambda e: e[0])[2] if score['parts'][idx[v]]['tev'] else None) for v in vids}
    tutti_keys = sorted({k for k in first.values() if k})
    t = mixes['tempo']; q = t['bpm'] * MA.BEATQ[t.get('beat') or 'quarter']
    # lost notes: pitched notes in the XML (chord notes included, tie ends excluded) vs. notes the audio step reads
    xr = etree.parse(xml).getroot()
    for k, p in enumerate(xr.findall('part')):
        n_xml = sum(1 for n in p.iter('note') if n.find('pitch') is not None and not any(x.get('type') == 'stop' for x in n.findall('tie')))
        n_mid = len(score['parts'][k]['tev'])
        if n_xml > n_mid and not MA.playback_order(spec): fails.append(f'MIDI: voice {vids[k]} has {n_xml} notes in the score but only {n_mid} are read for the audio (chord notes dropped?)')

    # MIDI file -> per track (note-on events, tempo, name)
    def read(path):
        m = mido.MidiFile(path); tr = []
        for track in m.tracks:
            now, ons, tempo, name = 0, [], None, None
            for msg in track:
                now += msg.time
                if msg.type == 'set_tempo' and tempo is None: tempo = mido.tempo2bpm(msg.tempo)
                if msg.type == 'track_name': name = msg.name
                if msg.type == 'note_on' and msg.velocity > 0: ons.append((now, msg.note, msg.channel))
            tr.append((ons, tempo, name))
        return tr

    # A MIDI file must carry the intended tempo, one track per voice, the starting-note intro and the same notes as the score
    def compare(path, tq, voices, intro_keys):
        rel = os.path.relpath(path, pkg)
        try: tr = read(path)
        except Exception as e: return [f'MIDI unreadable: {rel} ({e})']
        if len(tr) != 1 + len(voices): return [f'MIDI {rel}: {len(tr)-1} voice tracks, expected {len(voices)}']
        if tr[0][1] is None or abs(tr[0][1] - tq) > 0.05: return [f'MIDI {rel}: tempo {tr[0][1]} instead of {tq:.1f}']
        n_len, g_len = MA.sec2ticks(MA.INTRO['note_s'], tq), MA.sec2ticks(MA.INTRO['note_gap_s'], tq)
        intro = sorted(o for o in tr[0][0] if o[2] == 14)
        if [o[1] for o in intro] != intro_keys: return [f'MIDI {rel}: starting notes {[o[1] for o in intro]} instead of {intro_keys}']
        if any(abs(o[0] - k * (n_len + g_len)) > 2 for k, o in enumerate(intro)): return [f'MIDI {rel}: starting notes not evenly spaced']
        shift = (len(intro_keys) * (n_len + g_len) - g_len if intro_keys else 0) + MA.sec2ticks(MA.INTRO['gap_s'], tq) + start
        for j, v in enumerate(voices):
            got = sorted((o[0] - shift, o[1]) for o in tr[1 + j][0])
            exp = sorted((e[0], e[2]) for e in score['parts'][idx[v]]['tev'])
            if len(got) != len(exp): return [f'MIDI {rel}: voice {v} has {len(got)} notes, score has {len(exp)}']
            for (gt, gk), (et, ek) in zip(got, exp):
                if gk != ek or abs(gt - et) > 2: return [f'MIDI {rel}: voice {v} differs at tick {et} (note {ek} expected, {gk} at {gt} found)']
        return []

    n = 0; problems = []
    for sk in ('choir', 'piano'):
        for own in vids:
            for stage in ('solo', 'accomp', 'choir'):
                lay = mixes['stages'][stage][own]; voices = [x[0] for x in lay]
                for slow in ((False, True) if stage != 'choir' else (False,)):
                    base = os.path.join(pkg, fo['practice'], snd[sk], stg[stage]) + (os.sep + i18['slow'] if slow else '')
                    f = os.path.join(base, 'MIDI', f'{slug}_{stg[stage]}_{safe(mixes["names"][own])}_{snd[sk]}' + (f'_{i18["slow"]}' if slow else '') + '.mid')
                    if not os.path.exists(f): continue   # missing files are reported by the structure check
                    problems += compare(f, q * (mixes['tempo'].get('slow_pct', 75) / 100 if slow else 1), voices, [first[own]] if first[own] else []); n += 1
        f = os.path.join(pkg, fo['tutti'], snd[sk], f'{slug}_{i18["files"]["tutti"]}_{snd[sk]}.mid')
        if os.path.exists(f): problems += compare(f, q, vids, tutti_keys); n += 1
    fails.extend(problems[:8])
    if len(problems) > 8: fails.append(f'MIDI: {len(problems) - 8} more files with differences')
    return n


# Final gate: collects everything wrong with the package in `fails` (blocking) and `warns` (shown, not blocking)
def main():
    ap = argparse.ArgumentParser(); ap.add_argument('pkg'); ap.add_argument('spec'); ap.add_argument('--workdir', required=True)
    A = ap.parse_args(); pkg = A.pkg
    spec = json.load(open(A.spec, encoding='utf-8')); i18 = load_i18n(spec.get('language', 'en'))
    fo, snd, stg = i18['folders'], i18['sounds'], i18['stages']; slug = safe(spec['meta']['title'])
    fails, warns = [], []
    def need(path, what):
        if not glob.glob(path): fails.append(f'missing: {what} ({os.path.relpath(path, pkg)})')
    sc = os.path.join(pkg, fo['scores'])
    need(os.path.join(sc, '*.pdf'), 'score PDF')
    for k in ('choir', 'piano'):
        need(os.path.join(sc, f'{slug}_{snd[k]}.musicxml'), f'MusicXML {k}')
    need(os.path.join(pkg, fo['practice'], '*.pdf'), 'overview PDF')
    groups = {}
    for v in spec['voices']:
        vn = safe(v['name'])
        for k in ('choir', 'piano'):
            for s in ('solo', 'accomp', 'choir'):
                base = os.path.join(pkg, fo['practice'], snd[k], stg[s])
                for ext, sub in (('mp3', 'MP3'), ('mid', 'MIDI')):
                    need(os.path.join(base, sub, f'{slug}_{stg[s]}_{vn}_{snd[k]}.{ext}'), f'{s} {v["name"]} {k} {ext}')
                    if s != 'choir':
                        need(os.path.join(base, i18['slow'], sub, f'{slug}_{stg[s]}_{vn}_{snd[k]}_{i18["slow"]}.{ext}'), f'{s} slow {v["name"]} {k} {ext}')
                for f in glob.glob(os.path.join(base, 'MP3', '*.mp3')): groups.setdefault(s, []).append(f)
                for f in glob.glob(os.path.join(base, i18['slow'], 'MP3', '*.mp3')): groups.setdefault(s + '_slow', []).append(f)   # slow files: own group (other tempo)
    for k in ('choir', 'piano'):
        need(os.path.join(pkg, fo['tutti'], snd[k], '*.mp3'), f'tutti {k} mp3'); need(os.path.join(pkg, fo['tutti'], snd[k], '*.mid'), f'tutti {k} mid')
    for f in ('README.md', 'README.pdf', 'session_handoff.md', safe(i18['files']['protocol']) + '.md', safe(i18['files']['protocol']) + '.pdf',
              safe(i18['files_more']['corrections']) + '.md', safe(i18['files_more']['corrections']) + '.pdf'):
        need(os.path.join(pkg, f), f)
    # score PDF / layout
    for f in glob.glob(os.path.join(sc, '*.pdf')):
        for p in PdfReader(f).pages:
            w, h = float(p.mediabox.width), float(p.mediabox.height)
            if not (abs(w - 595) < 3 and abs(h - 842) < 3): fails.append(f'score page not A4 portrait ({w:.0f}×{h:.0f})'); break
    lays = glob.glob(os.path.join(sc, '*.layout.json')) + glob.glob(os.path.join(pkg, fo['tools'], 'layout.json'))
    if lays:
        L = json.load(open(lays[0]))
        if L['scale'] < L['min_scale']: fails.append(f"score too small: scale {L['scale']} < {L['min_scale']}")
        if min(L['page_fill']) < 0.8: fails.append(f"page not filled: {L['page_fill']}")
        if L.get('compressed'): fails.append('score systems over-compressed')
    else: warns.append('layout.json not found – readability not verified')
    for f in glob.glob(os.path.join(pkg, fo['practice'], '*.pdf')):
        r = PdfReader(f)
        if len(r.pages) != 1: fails.append(f'overview has {len(r.pages)} pages')
        w, h = float(r.pages[0].mediabox.width), float(r.pages[0].mediabox.height)
        if not (abs(w - 842) < 3 and abs(h - 595) < 3): fails.append('overview not A4 landscape')
    # lyrics consistency
    x = glob.glob(os.path.join(sc, f'{slug}_{snd["choir"]}.musicxml'))
    if x:
        r = etree.parse(x[0]).getroot(); texts = {}
        for p in r.findall('part'):
            V = {}
            for n in p.iter('note'):
                for l in n.findall('lyric'):
                    if l.findtext('text'): V.setdefault(l.get('number'), []).append(l.findtext('text'))
            texts[p.get('id')] = V
        ov = set(spec.get('lyrics', {}).get('voice_overrides', {}))
        ids = {f'P{k+1}': v['id'] for k, v in enumerate(spec['voices'])}
        ref = None
        for pid, V in texts.items():
            if ids[pid] in ov: continue
            if ref is None: ref = V
            elif V != ref: fails.append(f'lyrics differ in {ids[pid]} without a declared override')
        for pid, V in texts.items():
            if ids[pid] in ov and ref:
                for k2 in ref:
                    a = re.sub(r'\W', '', ''.join(ref[k2])); b = re.sub(r'\W', '', ''.join(V.get(k2, [])))
                    if a != b: warns.append(f'{ids[pid]} verse {k2}: words differ from the other voices (override) – check intended')
    # performance signs: repeats/endings equal in all voices, every hairpin and ending closed
    if x:
        try:
            import signs_report as SR
            res = SR.signs(x[0]); per_voice = {}
            for bar, per in res.items():
                for v, sg in per.items(): per_voice.setdefault(v, {})[bar] = sg
            for bar, per in sorted(res.items()):
                sets = {tuple(sorted(t for t in sg if t.startswith(('repeat', 'ending')))) for sg in per.values()}
                if len(sets) > 1: fails.append(f'signs: repeat/ending signs differ between voices in bar {bar}')
            for v, bars in per_voice.items():
                d = sum(1 for sg in bars.values() for t in sg if t in ('<', '>')) - sum(1 for sg in bars.values() for t in sg if t == 'wedge end')
                if d: fails.append(f'signs: {v}: hairpin starts and ends do not match ({d:+d})')
                o = sum(1 for sg in bars.values() for t in sg if t.startswith('ending') and t.endswith('start'))
                c = sum(1 for sg in bars.values() for t in sg if t.startswith('ending') and t.endswith(('stop', 'discontinue')))
                if o != c: fails.append(f'signs: {v}: {o} ending starts but {c} ends')
            dyn = {v: [t for bars in b.values() for t in bars if t in ('pp','p','mp','mf','f','ff','fff','ppp','sf','sfz','fp')] for v, b in per_voice.items()}
            if len({tuple(a) for a in dyn.values()}) > 1: warns.append('signs: dynamics differ between voices – check against the source (voice-specific marks are allowed)')
        except ImportError as e: warns.append(f'sign check skipped ({e})')
    # MIDI against the score
    n_midi = check_midi(pkg, spec, i18, os.path.join(sc, f'{slug}_{snd["choir"]}.musicxml'), fails, warns)
    # audio durations
    for fs in groups.values():
        fs = sorted(set(fs))   # the folder is globbed once per voice: count each file once
        ds = [dur(f) for f in fs]
        if not ds: continue
        med = statistics.median(ds)
        for f, d in zip(fs, ds):
            if d < 5 or abs(d - med) > 0.15 * med: fails.append(f'audio duration suspicious: {os.path.basename(f)} {d:.1f}s (median {med:.1f}s)')
    # names
    for root_, dirs, files in os.walk(pkg):
        for nm in dirs + files:
            if nm not in ('README.md', 'README.pdf') and safe(nm) != nm: fails.append(f'unsafe name: {nm}')
    print(f'{len(fails)} failure(s), {len(warns)} warning(s)')
    for f in fails: print('  FAIL', f)
    for w in warns: print('  WARN', w)
    log_check(A.workdir, 6, 'verify', 'fail' if fails else ('warn' if warns else 'pass'),
              ('; '.join(fails[:6]) if fails else 'structure, A4 layout, overview, lyrics, ' + (f'MIDI vs. score ({n_midi} files), ' if n_midi else '') + 'audio durations, names OK') + (f' | warnings: {"; ".join(warns[:3])}' if warns else ''))
    sys.exit(1 if fails else 0)

if __name__ == '__main__':
    main()
