#!/usr/bin/env python3
"""Convert an existing MusicXML file (e.g. an OMR draft or an earlier version) into a score.json
specification. Several voices on one staff (voice 1/2) become separate voices.

  python3 musicxml_to_spec.py in.musicxml score.json --voices "T1:Tenor 1,T2:Tenor 2,B1:Bass 1,B2:Bass 2"

Without --voices the voices are named in part/voice order (S1, S2, ...).
The result is a DRAFT: always proofread it against the PDF (references/transcription-guide.md).
"""
import json, sys, argparse, re
from lxml import etree
from score_schema import validate_spec

def pitch_str(n):
    p = n.find('pitch'); step = p.findtext('step'); alt = int(float(p.findtext('alter') or 0))
    return step + {-2: 'bb', -1: 'b', 0: '', 1: '#', 2: '##'}[alt] + p.findtext('octave')

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('xml'); ap.add_argument('out'); ap.add_argument('--voices')
    A = ap.parse_args()
    t = etree.parse(A.xml); r = t.getroot()
    parts = r.findall('part')
    div = int(r.find('.//divisions').text)
    tm = r.find('.//time'); time = [int(tm.findtext('beats')), int(tm.findtext('beat-type'))]
    fifths = int(r.find('.//key/fifths').text)
    # collect voice streams
    streams = []  # (part, voice, clef)
    for p in parts:
        vs = sorted({n.findtext('voice') or '1' for n in p.iter('note')})
        cl = p.find('.//clef'); sign = cl.findtext('sign') if cl is not None else 'G'
        octc = cl.findtext('clef-octave-change') if cl is not None else None
        clef = 'bass' if sign == 'F' else ('treble8' if octc == '-1' else 'treble')
        for v in vs: streams.append((p, v, clef))
    names = [x.split(':', 1) for x in A.voices.split(',')] if A.voices else [(f'S{i+1}', f'Stimme {i+1}') for i in range(len(streams))]
    if len(names) != len(streams):
        sys.exit(f'{len(streams)} voices found but {len(names)} names given')
    music = {}; lyr = {}; dirs = []; barlines = {}; tempo_text = None
    measures0 = parts[0].findall('measure')
    pickup = measures0[0].get('implicit') == 'yes'
    for (p, v, clef), (vid, vname) in zip(streams, names):
        bars = []; L = {}
        for bi, m in enumerate(p.findall('measure')):
            pos = 0; last = 0; toks = []
            for e in m:
                if e.tag == 'backup': pos -= int(e.findtext('duration')); continue
                if e.tag == 'forward': pos += int(e.findtext('duration')); continue
                if e.tag == 'direction' and v == (sorted({n.findtext('voice') or '1' for n in p.iter('note')})[0]):
                    for dt in e.findall('direction-type'):
                        if dt.find('dynamics') is not None:
                            dirs.append({'bar': bi, 'onset': pos, 'kind': 'dyn', 'value': dt.find('dynamics')[0].tag, '_v': vid})
                        if dt.find('wedge') is not None:
                            wv = dt.find('wedge').get('type')
                            dirs.append({'bar': bi, 'onset': pos, 'kind': 'wedge', 'value': {'crescendo': 'crescendo', 'diminuendo': 'diminuendo', 'stop': 'stop'}.get(wv, wv), '_v': vid})
                        if dt.find('words') is not None and (dt.findtext('words') or '').strip():
                            w = dt.findtext('words').strip()
                            if bi == 0 and tempo_text is None and dt.find('words').get('font-weight') == 'bold': tempo_text = w
                            else: dirs.append({'bar': bi, 'onset': pos, 'kind': 'words', 'value': w, '_v': vid})
                    continue
                if e.tag == 'barline':
                    bs = e.findtext('bar-style')
                    if bs: barlines[str(bi)] = bs
                    continue
                if e.tag != 'note': continue
                d = int(e.findtext('duration')); chord = e.find('chord') is not None
                st = last if chord else pos
                if not chord: last = pos; pos += d
                if (e.findtext('voice') or '1') != v or chord: continue
                if e.find('rest') is not None:
                    toks.append(f'r/{d}'); continue
                f = ''
                if any(x.get('type') == 'start' for x in e.findall('tie')): f += '~'
                for s in e.findall('notations/slur'):
                    dotted = s.get('line-type') == 'dotted'
                    if s.get('type') == 'stop': f += '}' if dotted else ')'
                for s in e.findall('notations/slur'):
                    dotted = s.get('line-type') == 'dotted'
                    if s.get('type') == 'start': f += '{' if dotted else '('
                if e.find('notations/fermata') is not None: f += '^'
                toks.append(f'{pitch_str(e)}/{d}{f}')
                for l in e.findall('lyric'):
                    tx = l.findtext('text')
                    if not tx: continue
                    tx = re.sub(r'^\d+\. ', '', tx)
                    syl = l.findtext('syllabic') or 'single'
                    L.setdefault(l.get('number') or '1', []).append((bi, st, tx + ('-' if syl in ('begin', 'middle') else '')))
            bars.append(' '.join(toks))
        music[vid] = bars; lyr[vid] = L
    # default lyrics per verse = voice with most syllables; differences become overrides
    verses = sorted({k for L in lyr.values() for k in L}, key=lambda x: int(x))
    default = {}; overrides = {}
    for k in verses:
        src = max(lyr, key=lambda vid: len(lyr[vid].get(k, [])))
        default[k] = lyr[src][k]
        dmap = {}
        for b, o, tx in default[k]: dmap.setdefault(b, set()).add((o, tx))
        for vid, L in lyr.items():
            if vid == src or k not in L: continue
            vmap = {}
            for b, o, tx in L[k]: vmap.setdefault(b, set()).add((o, tx))
            diff = [b for b in vmap if vmap[b] != dmap.get(b, set())]
            if diff:
                ov = overrides.setdefault(vid, {'bars': [], 'verses': {}})
                ov['bars'] = sorted(set(ov['bars']) | set(diff))
                ov['verses'][k] = ' | '.join(f'{b}:{o}:{tx}' for b, o, tx in L[k] if b in diff)
    # directions once per position/kind; voice assignment
    merged = {}
    for d in dirs:
        key = (d['bar'], d['onset'], d['kind'], d['value'])
        merged.setdefault(key, set()).add(d['_v'])
    allv = [n[0] for n in names]
    dlist = []
    for (b, o, k, v), vs in sorted(merged.items(), key=lambda x: (x[0][0], x[0][1])):
        dd = {'bar': b, 'onset': o, 'kind': k, 'value': v}
        if set(vs) != set(allv): dd['voices'] = sorted(vs, key=allv.index)
        dlist.append(dd)
    nb = len(measures0)
    if str(nb - 1) in barlines and barlines[str(nb - 1)] in ('light-heavy',): del barlines[str(nb - 1)]
    title = r.findtext('work/work-title') or r.findtext('movement-title') or ''
    meta = {'title': title}
    for c in r.findall('identification/creator'):
        meta[c.get('type')] = re.sub(r'^(Text|Satz|Musik|Worte|Melodie)\s*:\s*', '', c.text or '')
    spec = {'language': 'en', 'meta': meta, 'tempo': {'text': tempo_text, 'bpm': None, 'beat': None},
            'key_fifths': fifths, 'time': time, 'divisions': div, 'pickup': pickup,
            'voices': [{'id': vid, 'name': vn, 'clef': cl} for (vid, vn), (_, _, cl) in zip(names, streams)],
            'seating': [n[0] for n in names],
            'music': music,
            'lyrics': {'verses': {k: ' | '.join(f'{b}:{o}:{tx}' for b, o, tx in default[k]) for k in verses}, 'voice_overrides': overrides},
            'directions': dlist, 'barlines': barlines}
    validate_spec(spec, A.out)   # never hand a malformed draft to build_score.py
    json.dump(spec, open(A.out, 'w'), ensure_ascii=False, indent=1)
    print('spec written:', A.out, '| voices:', [n[0] for n in names], '| bars:', nb, '| verses:', verses, '| overrides:', list(overrides))

if __name__ == '__main__':
    main()
