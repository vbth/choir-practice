#!/usr/bin/env python3
"""List the performance signs of a MusicXML score per bar and voice, to tick off against the scan (Phase 4).

Usage: signs_report.py score.musicxml [--out signs.txt]
Signs: dynamics, hairpins (< > start/stop), words (rit., cresc., ...), repeat signs, endings, fermatas, tempo.
Exit code 0 always; problems are printed as 'CHECK:' lines (unequal signs between voices, hairpin without end,
ending without end). It does not read the scan; the comparison with the original stays with the proofreader.
"""
import sys, argparse
from lxml import etree

def signs(xml):
    r = etree.parse(xml).getroot(); names = {sp.get('id'): sp.findtext('part-name') for sp in r.iter('score-part')}
    res = {}
    for p in r.findall('part'):
        pid = names.get(p.get('id'), p.get('id'))
        for i, m in enumerate(p.findall('measure'), 1):
            s = res.setdefault(i, {}).setdefault(pid, [])
            for d in m.findall('direction'):
                for dt in d.findall('direction-type'):
                    if dt.find('dynamics') is not None: s.append(dt.find('dynamics')[0].tag)
                    if dt.find('wedge') is not None: s.append({'crescendo': '<', 'diminuendo': '>', 'stop': 'wedge end'}.get(dt.find('wedge').get('type'), '?'))
                    w = (dt.findtext('words') or '').strip()
                    if w: s.append(f'"{w}"')
                for snd in d.findall('sound'):
                    if snd.get('tempo'): s.append(f'tempo {snd.get("tempo")}')
            for b in m.findall('barline'):
                loc = b.get('location', 'right')
                if b.find('repeat') is not None: s.append(f'repeat {b.find("repeat").get("direction")} ({loc})')
                if b.find('ending') is not None: s.append(f'ending {b.find("ending").get("number")} {b.find("ending").get("type")}')
            if m.find('.//fermata') is not None: s.append('fermata')
    return res

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('xml'); ap.add_argument('--out')
    A = ap.parse_args(); res = signs(A.xml); lines, checks = [], []
    for bar in sorted(res):
        per = res[bar]
        if not any(per.values()): continue
        lines.append(f'bar {bar}: ' + ' | '.join(f'{v}: {", ".join(s) if s else "-"}' for v, s in per.items()))
        sets = {tuple(sorted(x for x in s if x.startswith(('repeat', 'ending')))) for s in per.values()}
        if len(sets) > 1: checks.append(f'CHECK: bar {bar}: repeat/ending signs differ between voices')
    for v in {v for per in res.values() for v in per}:
        depth = 0
        for bar in sorted(res):
            for x in res[bar].get(v, []):
                if x in ('<', '>'): depth += 1
                if x == 'wedge end': depth -= 1
        if depth != 0: checks.append(f'CHECK: {v}: hairpin start/end count does not match ({depth:+d})')
        opens = sum(1 for bar in res for x in res[bar].get(v, []) if x.endswith('start') and x.startswith('ending'))
        stops = sum(1 for bar in res for x in res[bar].get(v, []) if x.startswith('ending') and (x.endswith('stop') or x.endswith('discontinue')))
        if opens != stops: checks.append(f'CHECK: {v}: {opens} ending starts but {stops} ends')
    txt = '\n'.join(lines + checks) or 'no performance signs found'
    print(txt)
    if A.out: open(A.out, 'w', encoding='utf-8').write(txt)
    sys.exit(0)

if __name__ == '__main__': main()
