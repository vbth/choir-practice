#!/usr/bin/env python3
"""Rhythm data for the sound waves at the headphones (section "Üben" / "Practice"): docs/audio/waves.json

  python3 site/make_wave_timeline.py [--audio docs/audio]

Reads the 42 website recordings (docs/audio/*.mp3, needs ffmpeg and numpy) and writes per recording
  "o": note onsets as a flat list [ms, strength 0..100, ms, strength, ...]
  "l": one character per 50 ms, "1" while the recording is loud (RMS above -25 dB), else "0".
The page (site/build_site.py, function wvTick) reads A.currentTime and lets the three arcs per side flash at every onset and fade from the outside in,
so it needs neither Web Audio nor an AudioContext (works on every browser, never mutes the audio).

Onset = the level (RMS over 1024 samples, every 735 samples = 60 Hz) is rising and jumps more than 2.5 dB above its slow average (15 % per frame),
level above -45 dB, at least 150 ms after the previous onset; strength 0.55 + jump / 10 dB, at most 1. On the example recordings this finds the quarter
notes of the piano (every 400 ms) and 2 to 3 onsets per second in the choir. Run it after make_web_audio.py."""
import glob, json, os, subprocess, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SR, WIN, HOP = 44100, 1024, 735

def decode(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32)

def db_at(x, end):
    w = x[max(0, end - WIN):end]
    return 20 * np.log10(float(np.sqrt((w ** 2).mean())) + 1e-6)

def analyse(x):
    onsets, slow, last, prev = [], None, -1e9, None
    for end in range(WIN, len(x) + 1, HOP):
        db = db_at(x, end); slow = db if slow is None else slow
        flux = db - slow; ms = (end - WIN / 2) / SR * 1000   # centre of the window
        if flux > 2.5 and db > -45 and ms - last > 150 and (prev is None or db > prev):
            onsets += [int(round(ms)), int(round(min(1.0, 0.55 + flux / 10) * 100))]; last = ms
        slow += 0.15 * (db - slow); prev = db
    loud = ''.join('1' if db_at(x, int((j + 0.5) * 0.05 * SR) + WIN // 2) > -25 else '0' for j in range(int(len(x) / SR / 0.05)))
    return {'o': onsets, 'l': loud}

def main():
    ad = sys.argv[sys.argv.index('--audio') + 1] if '--audio' in sys.argv else os.path.join(HERE, '..', 'docs', 'audio')
    out = {}
    for p in sorted(glob.glob(os.path.join(ad, '*.mp3'))):
        name = os.path.basename(p)[:-4]; out[name] = analyse(decode(p)); print(f'{name:22s} {len(out[name]["o"]) // 2:4d} onsets')
    dest = os.path.join(ad, 'waves.json')
    with open(dest, 'w', encoding='utf-8') as f: json.dump(out, f, separators=(',', ':'))
    print('written:', os.path.relpath(dest, os.path.join(HERE, '..')), f'({os.path.getsize(dest) // 1024} KB, {len(out)} recordings)')

if __name__ == '__main__':
    main()
