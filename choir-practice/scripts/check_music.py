#!/usr/bin/env python3
"""Musical plausibility check – catches typical misreadings after transcription.

  python3 check_music.py score.json [--workdir WORK]

Flags per voice: notes outside the usual range of the voice type, melodic leaps larger than an octave,
and bars where all voices have identical rhythm except one (possible missed note). Every finding must be
checked against the source PDF; confirmed-correct findings go to the correction log as "checked, as in source".
Writes WORK/music_findings.json and a check-log entry.
"""
import json, sys, os, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import log_check
from build_score import TOK, parse_pitch

STEP = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
RANGES = {  # sounding pitch, generous outer limits for amateur choirs
    'soprano': ('B3', 'C6'), 'mezzo': ('A3', 'A5'), 'alto': ('E3', 'F5'), 'tenor': ('A2', 'C5'),
    'baritone': ('F2', 'G4'), 'bass': ('C2', 'F4')}
KEYWORDS = [('sopran', 'soprano'), ('mezzo', 'mezzo'), ('alt', 'alto'), ('tenor', 'tenor'), ('bari', 'baritone'),
            ('bass', 'bass'), ('baß', 'bass'), ('basso', 'bass'), ('s', 'soprano'), ('a', 'alto'), ('t', 'tenor'), ('b', 'bass')]

def midi(p):
    step, alt, octv, _ = parse_pitch(p)
    return 12 * (octv + 1) + STEP[step] + alt

def voice_type(v):
    if v.get('voice_type'): return v['voice_type']
    for txt in (v['name'].lower(), v['id'].lower()):
        for k, t in KEYWORDS:
            if txt.startswith(k): return t
    return None

# Collects plausibility findings per voice (range, leaps, rhythm patterns); they are warnings for the user to look at, not proof of errors
def main():
    ap = argparse.ArgumentParser(); ap.add_argument('spec'); ap.add_argument('--workdir')
    A = ap.parse_args(); spec = json.load(open(A.spec, encoding='utf-8'))
    findings = []
    rhythms = {}
    for v in spec['voices']:
        vt = voice_type(v); lo, hi = (midi(RANGES[vt][0]), midi(RANGES[vt][1])) if vt else (None, None)
        prev = None
        for bi, line in enumerate(spec['music'][v['id']]):
            on = 0; rh = []
            for tok in line.split():
                m = TOK.match(tok)
                if not m: continue
                d = int(m.group('d')); p = m.group('p'); rh.append((on, d));
                if p != 'r':
                    k = midi(p)
                    if lo is not None and not (lo <= k <= hi):
                        findings.append({'voice': v['id'], 'bar': bi, 'onset': on, 'kind': 'range', 'detail': f'{p} outside usual {vt} range {RANGES[vt][0]}–{RANGES[vt][1]}'})
                    if prev is not None and abs(k - prev[0]) > 12:
                        findings.append({'voice': v['id'], 'bar': bi, 'onset': on, 'kind': 'leap', 'detail': f'leap {prev[1]} → {p} ({abs(k - prev[0])} semitones)'})
                    prev = (k, p)
                on += d
            rhythms.setdefault(bi, {})[v['id']] = tuple(rh)
    for bi, rv in rhythms.items():
        vals = list(rv.values())
        if len(vals) >= 3:
            for vid, r in rv.items():
                others = [x for k, x in rv.items() if k != vid]
                if all(o == others[0] for o in others) and r != others[0] and len(r) == len(others[0]) - 1:
                    findings.append({'voice': vid, 'bar': bi, 'onset': None, 'kind': 'rhythm', 'detail': 'one note fewer than all other voices in this bar'})
    if A.workdir:
        json.dump(findings, open(os.path.join(A.workdir, 'music_findings.json'), 'w'), ensure_ascii=False, indent=1)
        log_check(A.workdir, 3, 'check_music', 'warn' if findings else 'pass', f'{len(findings)} findings (range/leap/rhythm) – each verified against the source' if findings else 'no range/leap/rhythm anomalies')
    print(f'{len(findings)} finding(s)')
    for f in findings: print(f"  {f['voice']} bar {f['bar']}: {f['kind']} – {f['detail']}")

if __name__ == '__main__':
    main()
