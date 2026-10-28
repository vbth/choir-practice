#!/usr/bin/env python3
"""Short statistics of one run: time per phase, scope, files, ZIP size, corrections, check rounds.

Usage: run_stats.py WORK --zip <delivery zip> [--out WORK/run_stats.md]
Reads WORK/checks.jsonl, WORK/score.json, WORK/docs.json. Time spent waiting for the user is taken from log entries
'question_asked' / 'answer_received' (log them with log_check.py around every AskUserQuestion) and shown separately.
Tokens are not measurable from inside the skill and are not reported.
"""
import sys, os, json, argparse, zipfile, datetime, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import read_checks

def mins(s): return f'{s / 60:.1f} min'

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('work'); ap.add_argument('--zip'); ap.add_argument('--out')
    A = ap.parse_args(); W = A.work; ent = read_checks(W)
    if not ent: sys.exit('no checks.jsonl entries found')
    t = [datetime.datetime.fromisoformat(e['time']) for e in ent]
    total = (t[-1] - t[0]).total_seconds(); wait = 0.0; asked = None; asks = 0
    for e, ts in zip(ent, t):
        if e['check'] == 'question_asked': asked = ts; asks += 1
        elif e['check'] == 'answer_received' and asked: wait += (ts - asked).total_seconds(); asked = None
    gaps = sorted(((t[i] - t[i - 1]).total_seconds(), ent[i]['check']) for i in range(1, len(ent)) if ent[i]['check'] not in ('question_asked', 'answer_received'))
    pkg = os.path.join(W, 'pkg')
    audio = sorted(os.path.getmtime(os.path.join(d, f)) for d, _, fs in os.walk(pkg) for f in fs if f.endswith(('.mp3', '.mid'))) if os.path.isdir(pkg) else []
    spec = json.load(open(os.path.join(W, 'score.json'), encoding='utf-8')) if os.path.exists(os.path.join(W, 'score.json')) else {}
    docs = json.load(open(os.path.join(W, 'docs.json'), encoding='utf-8')) if os.path.exists(os.path.join(W, 'docs.json')) else {}
    voices = spec.get('voices', []); bars = len(spec.get('music', {}).get(voices[0]['id'], [])) if voices else 0
    verses = len(spec.get('lyrics', {}).get('verses', {}))
    cor = collections.Counter(c.get('status') for c in docs.get('corrections', []))
    res = collections.Counter(e['result'] for e in ent)
    rounds = collections.Counter(e['check'] for e in ent if e['check'] not in ('question_asked', 'answer_received'))
    again = {k: v for k, v in rounds.items() if v > 1}
    L = ['# Run statistics', '',
         f'- Time from first to last log entry: {mins(total)}; of that waiting for you: {mins(wait)} ({asks} question(s)); working time: {mins(total - wait)}',
         '- Longest gaps between log entries (they include waiting, pauses and unlogged work, so they are not run times): ' + ', '.join(f'until {c}: {mins(g)}' for g, c in gaps[-3:][::-1]),
         (f'- Audio generation (file times, first to last file): {mins(audio[-1] - audio[0])}' if len(audio) > 1 else '- Audio generation: file times not available'),
         f'- Scope: {len(voices)} voices, {bars} bars, {verses} verse(s)',
         '- Checks: ' + ', '.join(f'{k} {v}' for k, v in res.items()) + (f'; repeated checks (rounds): {again}' if again else ''),
         f'- Corrections: {sum(cor.values())} (' + ', '.join(f'{k} {v}' for k, v in cor.items()) + ')']
    if A.zip and os.path.exists(A.zip):
        z = zipfile.ZipFile(A.zip); sz = collections.Counter(); cnt = collections.Counter()
        for i in z.infolist():
            if i.is_dir(): continue
            ext = os.path.splitext(i.filename)[1].lower() or 'other'; sz[ext] += i.compress_size; cnt[ext] += 1
        L.append(f'- ZIP: {os.path.getsize(A.zip) / 1e6:.1f} MB, {sum(cnt.values())} files; by type: ' + ', '.join(f'{k} {cnt[k]}x {v / 1e6:.1f} MB' for k, v in sz.most_common(6)))
    L.append('- Tokens: not measured by the skill')
    txt = '\n'.join(L); print(txt)
    open(A.out or os.path.join(W, 'run_stats.md'), 'w', encoding='utf-8').write(txt + '\n')

if __name__ == '__main__': main()
