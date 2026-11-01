#!/usr/bin/env python3
"""Compare the syllables you read in the source with the built score, bar by bar.

Usage: check_lyrics_order.py score.musicxml source_read.json [--part 1]
source_read.json (written by you from the source crops, Phase 4 pass 3):
  {"1": {"2": ["ei", "nem", "kuehl", "len"], "3": ["Grun", "de,", "da"]}, "2": {...}}
  verse number -> measure number (1-based, MusicXML measure order, pickup = 1) -> syllables in note order.
Hyphens, case and punctuation are ignored. Every line starting with 'DIFF' is a finding: a syllable on the wrong
note, a missing or extra syllable, or a swapped word. Exit code 1 if any DIFF. It cannot find a mistake you made
when reading the source - it compares two readings.
"""
import sys, json, re, argparse
from lxml import etree

def norm(t): return re.sub(r'[\W_]+', '', t.lower())

# Syllables of the built score as {verse: {bar: [text, ...]}}
def built(xml, part):
    r = etree.parse(xml).getroot(); p = r.findall('part')[part - 1]; out = {}
    for i, m in enumerate(p.findall('measure'), 1):
        for n in m.findall('note'):
            for l in n.findall('lyric'):
                if l.findtext('text'): out.setdefault(l.get('number'), {}).setdefault(i, []).append(l.findtext('text'))
    return out

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('xml'); ap.add_argument('read'); ap.add_argument('--part', type=int, default=1)
    A = ap.parse_args(); b = built(A.xml, A.part); src = json.load(open(A.read, encoding='utf-8')); bad = 0
    for verse in sorted(set(b) | set(src), key=lambda x: int(x)):
        bars = sorted({int(k) for k in b.get(verse, {})} | {int(k) for k in src.get(verse, {})})
        for bar in bars:
            got = [norm(x) for x in b.get(verse, {}).get(bar, [])]; exp = [norm(x) for x in src.get(verse, {}).get(str(bar), [])]
            if got != exp:
                bad += 1; print(f'DIFF verse {verse} bar {bar}: source {exp} / build {got}')
    print(f'{bad} difference(s)' if bad else 'no differences')
    sys.exit(1 if bad else 0)

if __name__ == '__main__': main()
