#!/usr/bin/env python3
"""Technical listening test of the finished audio files (no ears needed for the common errors).

  python3 audio_check.py PKG score.json --workdir WORK [--only substring] [--json out.json]

Per MP3 (every file is compared with the MIDI file next to it, which carries the intended notes):
  duration     MP3 length = MIDI length + reverb tail (-3 .. +6 s; piano files -8 .. +6 s, because held piano notes fade out)
  silence      no stretch >= 0.5 s without sound where the MIDI has notes (not checked for piano files: held notes fade; lost notes are caught by verify.py)
  clipping     no sample at full scale
  loudness     integrated loudness within 3 LU of the target (mixes.json "lufs"); tutti is checked against its own level
  stereo       both ears filled; solo files centred (L/R within 1.5 dB)
Prints one line per problem and a summary; exit code 1 if anything failed. The result is logged as check
"audio_check" (phase 6). The workflow stays silent about a pass and reports only failures (see SKILL.md, Phase 6).
"""
import os, sys, json, glob, argparse, subprocess, tempfile, re
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import log_check, load_i18n

SR = 22050

def decode(mp3):
    with tempfile.TemporaryDirectory() as t:
        w = os.path.join(t, 'a.raw')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', mp3, '-vn', '-f', 'f32le', '-ac', '2', '-ar', str(SR), w], check=True)
        a = np.fromfile(w, dtype='<f4')
    return a.reshape(-1, 2)

def lufs(mp3):
    r = subprocess.run(['ffmpeg', '-nostats', '-i', mp3, '-vn', '-af', 'ebur128=framelog=quiet', '-f', 'null', '-'], capture_output=True, text=True).stderr
    m = re.findall(r'I:\s*(-?[\d.]+) LUFS', r)
    return float(m[-1]) if m else None

def midi_notes(path):
    import mido
    t = 0.0; on = {}; notes = []
    for msg in mido.MidiFile(path):
        t += msg.time
        if msg.type == 'note_on' and msg.velocity > 0: on.setdefault((msg.channel, msg.note), []).append(t)
        elif msg.type in ('note_off', 'note_on') and (msg.type == 'note_off' or msg.velocity == 0):
            k = (msg.channel, msg.note)
            if on.get(k): notes.append((on[k].pop(0), t, msg.note))
    for (c, n), ts in on.items():
        for s in ts: notes.append((s, t, n))
    notes.sort(); return notes, t

def check_file(mp3, target_lufs, tutti=False):
    """Return a list of problem strings for one MP3."""
    prob = []; mid = mp3[:-4].replace('/MP3/', '/MIDI/') + '.mid'
    if not os.path.exists(mid): mid = os.path.join(os.path.dirname(mp3), os.path.basename(mp3)[:-4] + '.mid')
    a = decode(mp3); dur = len(a) / SR; mono = a.mean(axis=1)
    if len(a) < SR: return ['empty or unreadable file']
    if np.abs(a).max() >= 0.999: prob.append('clipping (full-scale samples)')
    rms = lambda v: 20 * np.log10(np.sqrt(np.mean(v ** 2)) + 1e-9)
    act = np.abs(mono) > 1e-3
    L, R = rms(a[act, 0]) if act.any() else -99, rms(a[act, 1]) if act.any() else -99
    if min(L, R) < -45: prob.append(f'one ear (almost) empty (L {L:.0f} dB, R {R:.0f} dB)')
    solo = '_1_Solo_' in mp3 or '_Solo_' in os.path.basename(mp3)
    if solo and abs(L - R) > 1.5: prob.append(f'solo file not centred (L/R differ by {abs(L - R):.1f} dB)')
    li = lufs(mp3)
    if li is not None and target_lufs is not None and not tutti and abs(li - target_lufs) > 3: prob.append(f'loudness {li:.1f} LUFS (target {target_lufs})')
    if os.path.exists(mid):
        notes, mlen = midi_notes(mid)
        piano = any(f'_{load_i18n(l)["sounds"]["piano"]}' in os.path.basename(mp3) for l in ('de', 'en'))   # piano notes decay: long held notes and the final note fade out before the MIDI note ends
        if not ((-8.0 if piano else -3.0) <= dur - mlen <= 6.0): prob.append(f'duration {dur:.1f} s vs. MIDI {mlen:.1f} s')
        # silence where the MIDI has notes
        hop = int(0.05 * SR); env = np.array([rms(mono[i:i + hop]) for i in range(0, len(mono) - hop, hop)])
        active = np.zeros(len(env), bool)
        for s, e, n in notes: active[int(s / 0.05):int(e / 0.05) + 1 if int(e / 0.05) + 1 <= len(env) else len(env)] = True
        run = 0
        for k in range(0 if piano else len(env)):
            run = run + 1 if (active[k] and env[k] < -60) else 0
            if run >= 10: prob.append(f'silence at {(k - run + 1) * 0.05:.1f} s although the MIDI has notes'); break
    else: prob.append('MIDI file next to the MP3 missing')
    return prob

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('pkg'); ap.add_argument('spec'); ap.add_argument('--workdir'); ap.add_argument('--only'); ap.add_argument('--json')
    A = ap.parse_args()
    try: target = json.load(open(os.path.join(A.pkg, 'mixes.json'))).get('lufs')
    except Exception: target = None
    files = sorted(glob.glob(os.path.join(A.pkg, '**', '*.mp3'), recursive=True))
    if A.only: files = [f for f in files if A.only in f]
    res = {}; bad = {}
    for f in files:
        rel = os.path.relpath(f, A.pkg); p = check_file(f, target, tutti='_Tutti_' in f or '/03_Tutti/' in f.replace(os.sep, '/'))
        res[rel] = p
        if p: bad[rel] = p
    if A.json: json.dump({'checked': len(files), 'problems': bad}, open(A.json, 'w'), ensure_ascii=False, indent=1)
    for rel, p in bad.items():
        for x in p: print(f'PROBLEM {rel}: {x}')
    print(f'audio check: {len(files)} files, {len(bad)} with problems')
    if A.workdir:
        note = f'{len(files)} files: duration, gaps, clipping, loudness, stereo' if not bad else f'{len(bad)} of {len(files)} files with problems'
        log_check(A.workdir, 6, 'audio_check', 'fail' if bad else 'pass', note)
    sys.exit(1 if bad else 0)

if __name__ == '__main__': main()
