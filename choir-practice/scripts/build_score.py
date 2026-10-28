#!/usr/bin/env python3
"""Build MusicXML from a score specification (score.json, see references/score-spec.md):
one voice per staff, lyrics under every staff, verse numbers, slurs/ties, dynamics, header credits.

  python3 build_score.py score.json out.musicxml [--workdir WORK]

Validates: bar lengths per voice (incl. time-signature changes), every lyric syllable hits a note,
ties connect equal pitches, all voices have the same number of bars. Errors are listed with
voice/bar/onset and the script exits with code 1. With --workdir the result is logged to checks.jsonl.
"""
import json, sys, re, argparse, os
from lxml import etree
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import load_i18n, log_check, repeat_endings, repeat_times, skill_version

CLEFS = {'treble': ('G', '2', None), 'treble8': ('G', '2', '-1'), 'bass': ('F', '4', None),
         'alto': ('C', '3', None), 'tenor': ('C', '4', None)}
TOK = re.compile(r'^(?P<p>r|[A-G](?:##|bb|#|b|n)?-?\d)/(?P<d>\d+)(?P<f>[~(){}^]*)$')
ALTER = {'': 0, 'n': 0, '#': 1, '##': 2, 'b': -1, 'bb': -2}
SHARPS, FLATS = 'FCGDAEB', 'BEADGCF'

def note_type(dur, div):
    q = dur / div
    table = [(4, 'whole', 0), (6, 'whole', 1), (7, 'whole', 2), (2, 'half', 0), (3, 'half', 1), (3.5, 'half', 2),
             (1, 'quarter', 0), (1.5, 'quarter', 1), (1.75, 'quarter', 2), (0.5, 'eighth', 0), (0.75, 'eighth', 1),
             (0.875, 'eighth', 2), (0.25, '16th', 0), (0.375, '16th', 1), (0.125, '32nd', 0), (0.1875, '32nd', 1)]
    for v, t, dots in table:
        if abs(q - v) < 1e-9: return t, dots
    raise ValueError(f'duration {dur} (divisions={div}) is not a single note value – split it into tied notes')

def key_alters(fifths):
    return {s: 1 for s in SHARPS[:fifths]} if fifths > 0 else {s: -1 for s in FLATS[:-fifths]}

def parse_pitch(p):
    m = re.match(r'^([A-G])(##|bb|#|b|n)?(-?\d)$', p)
    acc = m.group(2) or ''
    return m.group(1), ALTER[acc], int(m.group(3)), acc

def bar_len(time, div):
    return int(time[0] * div * 4 / time[1])

def timeline(spec, nbars):
    """Per bar: (time, key_fifths) honouring spec['changes'] = {"bar": {"time": [3,4], "key_fifths": 0}}."""
    t, k = spec['time'], spec['key_fifths']; ch = {int(b): v for b, v in spec.get('changes', {}).items()}
    out = []
    for b in range(nbars):
        if b in ch:
            t = ch[b].get('time', t); k = ch[b].get('key_fifths', k)
        out.append((t, k))
    return out

def parse_voice(spec, vid, tl, errors):
    div = spec['divisions']; bars = spec['music'][vid]; nb = len(bars); out = []
    for bi, line in enumerate(bars):
        notes = []; on = 0
        for tok in line.split():
            m = TOK.match(tok)
            if not m:
                errors.append(f'{vid} bar {bi}: cannot parse token "{tok}"'); continue
            d = int(m.group('d')); f = m.group('f'); p = m.group('p')
            notes.append({'onset': on, 'dur': d, 'rest': p == 'r', 'pitch': None if p == 'r' else p, 'tie': '~' in f,
                          'slur_start': f.count('('), 'slur_end': f.count(')'), 'dslur_start': f.count('{'),
                          'dslur_end': f.count('}'), 'fermata': '^' in f, 'bar': bi, 'tie_stop': False})
            on += d
        blen = bar_len(tl[bi][0], div)
        if spec.get('pickup') and bi == 0: pass
        elif bi == nb - 1:
            if on > blen: errors.append(f'{vid} bar {bi}: length {on} > {blen}')
        elif on != blen:
            errors.append(f'{vid} bar {bi}: length {on}, expected {blen}')
        out.append(notes)
    flat = [n for b in out for n in b]
    for i, n in enumerate(flat):
        if n['tie']:
            if i + 1 >= len(flat) or flat[i + 1]['rest'] or flat[i + 1]['pitch'] != n['pitch']:
                errors.append(f"{vid} bar {n['bar']}: tie ~ without an equal following note")
            else:
                flat[i + 1]['tie_stop'] = True
    return out

def parse_lyric_tokens(s):
    res = []
    for item in (s or '').split('|'):
        item = item.strip()
        if item:
            bar, on, tok = item.split(':', 2); res.append((int(bar), int(on), tok.strip()))
    return res

def syllabify(tokens):
    out = {}; prev_open = False
    for bar, on, tok in sorted(tokens, key=lambda x: (x[0], x[1])):
        opened = tok.endswith('-') and len(tok) > 1; text = tok[:-1] if opened else tok
        syl = ('middle' if prev_open else 'begin') if opened else ('end' if prev_open else 'single')
        out[(bar, on)] = [text, syl]; prev_open = opened
    return out

def lyrics_for_voice(spec, vid):
    L = spec.get('lyrics', {})
    verses = {k: parse_lyric_tokens(v) for k, v in L.get('verses', {}).items()}
    ov = L.get('voice_overrides', {}).get(vid)
    if ov:
        ob = set(ov['bars'])
        for k, v in ov.get('verses', {}).items():
            verses[k] = [t for t in verses.get(k, []) if t[0] not in ob] + parse_lyric_tokens(v)
    res = {k: syllabify(v) for k, v in verses.items()}
    if len(res) > 1 and L.get('number_verses', True):
        for k, d in res.items():
            if d:
                first = min(d)
                if not d[first][0].startswith(f'{k}.'): d[first][0] = f'{k}. ' + d[first][0]
    return res

def E(tag, text=None, **attr):
    e = etree.Element(tag, **{k.replace('_', '-'): str(v) for k, v in attr.items()})
    if text is not None: e.text = str(text)
    return e

def build(spec):
    errors, warns = [], []
    div = spec['divisions']; voices = spec['voices']; vids = [v['id'] for v in voices]
    nbars = len(spec['music'][vids[0]])
    for v in vids:
        if len(spec['music'][v]) != nbars: errors.append(f'{v}: {len(spec["music"][v])} bars, expected {nbars}')
    tl = timeline(spec, nbars)
    parsed = {v: parse_voice(spec, v, tl, errors) for v in vids}
    meta = spec.get('meta', {}); i18 = load_i18n(spec.get('language', 'en'))
    offset = spec.get('bar_number_offset', 0)
    root = E('score-partwise', version='4.0')
    w = etree.SubElement(root, 'work'); etree.SubElement(w, 'work-title').text = meta.get('title', '')
    ident = etree.SubElement(root, 'identification')
    for t in ('composer', 'arranger', 'lyricist'):
        if meta.get(t): ident.append(E('creator', meta[t], type=t))
    enc = etree.SubElement(ident, 'encoding'); etree.SubElement(enc, 'software').text = 'choir-practice ' + skill_version()
    d = etree.SubElement(root, 'defaults'); sc = etree.SubElement(d, 'scaling')
    etree.SubElement(sc, 'millimeters').text = '7'; etree.SubElement(sc, 'tenths').text = '40'
    pl = etree.SubElement(d, 'page-layout'); etree.SubElement(pl, 'page-height').text = '1697'; etree.SubElement(pl, 'page-width').text = '1200'
    CV = i18['cover']   # same pattern as the header line of the score pages: "Name (Text)" left, "Name (Musik)" right
    right = f"{meta['composer']} ({CV['composer']})" if meta.get('composer') else ''
    if meta.get('arranger'): right = (right + ', ' if right else '') + f"{meta['arranger']} ({i18['credit_arr']})"
    left = f"{meta['lyricist']} ({CV['lyricist']})" if meta.get('lyricist') else ''
    for txt, j, x, y, sz in ((meta.get('title', ''), 'center', 600, 1640, 24), (meta.get('subtitle', ''), 'center', 600, 1600, 12),
                             (left, 'left', 70, 1590, 11), (right, 'right', 1130, 1590, 11)):
        if txt:
            cr = etree.SubElement(root, 'credit', page='1')
            cr.append(E('credit-words', txt, justify=j, halign=j, valign='top', font_size=sz, default_x=x, default_y=y))
    plist = etree.SubElement(root, 'part-list')
    g = etree.SubElement(plist, 'part-group', type='start', number='1')
    etree.SubElement(g, 'group-symbol').text = 'bracket'; etree.SubElement(g, 'group-barline').text = 'yes'
    for i, v in enumerate(voices, 1):
        sp = etree.SubElement(plist, 'score-part', id=f'P{i}')
        etree.SubElement(sp, 'part-name').text = v['name']; etree.SubElement(sp, 'part-abbreviation').text = v.get('abbr', v['id'])
        si = etree.SubElement(sp, 'score-instrument', id=f'P{i}-I1'); etree.SubElement(si, 'instrument-name').text = v['name']
        mi = etree.SubElement(sp, 'midi-instrument', id=f'P{i}-I1')
        etree.SubElement(mi, 'midi-channel').text = str(i); etree.SubElement(mi, 'midi-program').text = '53'
    etree.SubElement(plist, 'part-group', type='stop', number='1')
    rep_fwd, rep_bwd, end_start, end_stop = set(), {}, {}, {}
    for r in spec.get('repeats') or []:
        rep_fwd.add(r['start']); ends = repeat_endings(r)
        if ends:
            ends = sorted(ends, key=lambda e: e[1])
            for k, (ps, a, b) in enumerate(ends):
                end_start[a] = ','.join(str(x) for x in ps)
                end_stop[b] = (end_start[a], 'stop' if k < len(ends) - 1 else 'discontinue')
                if k < len(ends) - 1: rep_bwd[b] = 0
        else: rep_bwd[r['end']] = repeat_times(r) if repeat_times(r) > 2 else 0
    dirs = spec.get('directions', []); barlines = {int(k): v for k, v in spec.get('barlines', {}).items()}
    tempo = spec.get('tempo', {}); changes = {int(b): v for b, v in spec.get('changes', {}).items()}
    for i, v in enumerate(voices, 1):
        vid = v['id']; part = etree.SubElement(root, 'part', id=f'P{i}')
        lyr = lyrics_for_voice(spec, vid); used = {k: set() for k in lyr}; notes_el = []
        for bi, bar in enumerate(parsed[vid]):
            m = etree.SubElement(part, 'measure', number=str(bi + offset))
            if bi == 0 and spec.get('pickup'): m.set('implicit', 'yes')
            mnum = bi + 1
            if bi == 0 or bi in changes:
                at = etree.SubElement(m, 'attributes')
                if bi == 0: etree.SubElement(at, 'divisions').text = str(div)
                t, kf = tl[bi]
                if bi == 0 or 'key_fifths' in changes.get(bi, {}):
                    k = etree.SubElement(at, 'key'); etree.SubElement(k, 'fifths').text = str(kf)
                if bi == 0 or 'time' in changes.get(bi, {}):
                    tt = etree.SubElement(at, 'time'); etree.SubElement(tt, 'beats').text = str(t[0]); etree.SubElement(tt, 'beat-type').text = str(t[1])
                if bi == 0:
                    sign, line, oc = CLEFS[v.get('clef', 'treble')]
                    c = etree.SubElement(at, 'clef'); etree.SubElement(c, 'sign').text = sign; etree.SubElement(c, 'line').text = line
                    if oc: etree.SubElement(c, 'clef-octave-change').text = oc
                if bi == 0 and i == 1 and tempo.get('text'):
                    dd = E('direction', placement='above'); dt = etree.SubElement(dd, 'direction-type')
                    dt.append(E('words', tempo['text'], font_weight='bold')); m.append(dd)
            kal = key_alters(tl[bi][1])
            bar_dirs = [x for x in dirs if x['bar'] == bi and ('voices' not in x or vid in x['voices'])]
            blen = sum(n['dur'] for n in bar)
            def dir_el(x):
                dd = E('direction', placement=x.get('placement', 'above')); dt = etree.SubElement(dd, 'direction-type')
                if x['kind'] == 'dyn': etree.SubElement(etree.SubElement(dt, 'dynamics'), x['value'])
                elif x['kind'] == 'words': dt.append(E('words', x['value'], font_style='italic'))
                elif x['kind'] == 'wedge': dt.append(E('wedge', type=x['value'], number='1'))
                return dd
            acc_state = {}
            for n in bar:
                for x in bar_dirs:
                    if x.get('onset') == n['onset']: m.append(dir_el(x))
                ne = etree.SubElement(m, 'note')
                if n['rest']: etree.SubElement(ne, 'rest')
                else:
                    step, alt, octv, acc = parse_pitch(n['pitch'])
                    p = etree.SubElement(ne, 'pitch'); etree.SubElement(p, 'step').text = step
                    if alt: etree.SubElement(p, 'alter').text = str(alt)
                    etree.SubElement(p, 'octave').text = str(octv)
                etree.SubElement(ne, 'duration').text = str(n['dur'])
                if not n['rest']:
                    if n['tie_stop']: ne.append(E('tie', type='stop'))
                    if n['tie']: ne.append(E('tie', type='start'))
                etree.SubElement(ne, 'voice').text = '1'
                try: ty, dots = note_type(n['dur'], div)
                except ValueError as ex: errors.append(f'{vid} bar {bi}: {ex}'); ty, dots = 'quarter', 0
                etree.SubElement(ne, 'type').text = ty
                for _ in range(dots): etree.SubElement(ne, 'dot')
                if not n['rest']:
                    keyp = (step, octv); expect = acc_state.get(keyp, kal.get(step, 0))
                    if alt != expect or (acc == 'n' and expect != 0):
                        ne.append(E('accidental', {2: 'double-sharp', 1: 'sharp', 0: 'natural', -1: 'flat', -2: 'flat-flat'}[alt]))
                    acc_state[keyp] = alt
                nots = []
                if not n['rest']:
                    if n['tie_stop']: nots.append(E('tied', type='stop'))
                    if n['tie']: nots.append(E('tied', type='start'))
                nots += [E('slur', type='stop', number='1') for _ in range(n['slur_end'])]
                nots += [E('slur', type='stop', number='2') for _ in range(n['dslur_end'])]
                nots += [E('slur', type='start', number='1', placement='above') for _ in range(n['slur_start'])]
                nots += [E('slur', type='start', number='2', placement='above', line_type='dotted') for _ in range(n['dslur_start'])]
                if n['fermata']: nots.append(E('fermata', type='upright'))
                if nots:
                    nn = etree.SubElement(ne, 'notations')
                    for x in nots: nn.append(x)
                notes_el.append((n, ne))
            for x in bar_dirs:
                if x.get('onset') == 'end' or (isinstance(x.get('onset'), int) and x['onset'] >= blen): m.append(dir_el(x))
            bl = barlines.get(bi) or ('light-heavy' if bi == nbars - 1 else None)
            if mnum in rep_bwd and not bl: bl = 'light-heavy'
            if bl or mnum in end_stop or mnum in rep_bwd:
                b = etree.SubElement(m, 'barline', location='right')
                if bl: etree.SubElement(b, 'bar-style').text = bl
                if mnum in end_stop: etree.SubElement(b, 'ending', number=end_stop[mnum][0], type=end_stop[mnum][1])
                if mnum in rep_bwd:
                    rp = etree.SubElement(b, 'repeat', direction='backward')
                    if rep_bwd[mnum]: rp.set('times', str(rep_bwd[mnum]))
            if mnum in rep_fwd or mnum in end_start:
                b = etree.Element('barline', location='left')
                if mnum in rep_fwd and mnum > 1: etree.SubElement(b, 'bar-style').text = 'heavy-light'
                if mnum in end_start: etree.SubElement(b, 'ending', number=end_start[mnum], type='start')
                if mnum in rep_fwd: etree.SubElement(b, 'repeat', direction='forward')
                m.insert(0, b)
        for vk, L in lyr.items():
            chain, cur = [], None
            def close():
                nonlocal chain, cur
                if cur and chain and cur[2] in ('single', 'end'):
                    cur[1].append(E('extend', type='start'))
                    for kk, ne2 in enumerate(chain):
                        l2 = E('lyric', number=vk); l2.append(E('extend', type='stop' if kk == len(chain) - 1 else 'continue')); ne2.append(l2)
                chain, cur = [], None
            for n, ne in notes_el:
                if n['rest']: close(); continue
                key = (n['bar'], n['onset'])
                if key in L:
                    close(); txt, syl = L[key]; used[vk].add(key)
                    l = E('lyric', number=vk); l.append(E('syllabic', syl)); l.append(E('text', txt)); ne.append(l)
                    cur = (ne, l, syl)
                    if n['tie_stop']: warns.append(f'{vid} verse {vk} bar {key[0]}: syllable on a tied-over note')
                elif cur: chain.append(ne)
            close()
            for k2 in sorted(set(L) - used[vk]):
                errors.append(f'{vid} verse {vk}: syllable "{L[k2][0]}" at bar {k2[0]}, onset {k2[1]} hits no note')
    return root, errors, warns

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('spec'); ap.add_argument('out'); ap.add_argument('--workdir')
    A = ap.parse_args()
    spec = json.load(open(A.spec, encoding='utf-8'))
    root, errors, warns = build(spec)
    for w in warns: print('note:', w)
    if errors:
        print(f'{len(errors)} error(s):'); [print('  ' + e) for e in errors]
        if A.workdir: log_check(A.workdir, 2, 'build_score', 'fail', f'{len(errors)} errors: ' + '; '.join(errors[:5]))
        sys.exit(1)
    etree.ElementTree(root).write(A.out, encoding='UTF-8', xml_declaration=True, pretty_print=True,
        doctype='<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 4.0 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">')
    counts = {}
    for p in root.findall('part'):
        V = {}
        for ne in p.iter('note'):
            for l in ne.findall('lyric'):
                if l.findtext('text'): V[l.get('number')] = V.get(l.get('number'), 0) + 1
        counts[p.get('id')] = V
    print('MusicXML written:', A.out); print('syllables per part/verse:', counts)
    if A.workdir: log_check(A.workdir, 2, 'build_score', 'pass', f'bars/lyrics consistent; syllables {counts}' + (f'; {len(warns)} notes' if warns else ''))

if __name__ == '__main__':
    main()
