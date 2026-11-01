#!/usr/bin/env python3
"""Create the editable score files in two playback versions (choir and piano) as MusicXML:

  python3 make_scores.py final.musicxml outdir --slug Title --lang de [--workdir WORK]

Input should be the MusicXML written by render_score.py --write-xml (it carries the chosen system breaks).
Output names come from the language pack: <slug>_<Choir>.musicxml, <slug>_<Piano>.musicxml.
(No MuseScore files: the MusicXML opens in every notation program.)
"""
import os, sys, argparse
from lxml import etree
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import load_i18n, log_check

PROGRAMS = {'choir': 53, 'piano': 1}   # MusicXML midi-program is 1-based: 53 = Choir Aahs, 1 = Grand Piano
# Notation programs choose the playback sound by instrument id, not by MIDI program. The MusicXML
# <instrument-sound> sets that id on import; without it both versions sound the same.
VOICE_WORDS = [('sopran', 'voice.soprano'), ('mezzo', 'voice.mezzo-soprano'), ('alt', 'voice.alto'),
               ('tenor', 'voice.tenor'), ('barit', 'voice.baritone'), ('bass', 'voice.bass'), ('baß', 'voice.bass')]

# Picks the vocal sound (soprano/alto/tenor/bass) from the part name, falling back to the clef
def voice_sound(name, clef_sign, clef_oct):
    n = (name or '').lower()
    for w, snd in VOICE_WORDS:
        if w in n: return snd
    if clef_sign == 'F': return 'voice.bass'
    if clef_sign == 'G' and clef_oct == '-1': return 'voice.tenor'
    return 'voice.soprano'

def variant(src, out, program, mm=5.2):
    """Set playback program, notation-program-friendly page layout (A4, 5.2 mm per 40 tenths), credits positions."""
    t = etree.parse(src); r = t.getroot()
    for mp in r.iter('midi-program'): mp.text = str(program)
    for sp in r.iter('score-part'):
        part = r.find(f"part[@id='{sp.get('id')}']"); clef = part.find('.//clef') if part is not None else None
        snd = 'keyboard.piano' if program == PROGRAMS['piano'] else voice_sound(
            sp.findtext('part-name'), clef.findtext('sign') if clef is not None else None,
            clef.findtext('clef-octave-change') if clef is not None else None)
        for si in sp.iter('score-instrument'):
            old = si.find('instrument-sound')
            if old is not None: si.remove(old)
            e = etree.Element('instrument-sound'); e.text = snd
            nm = si.find('instrument-name'); (nm.addnext(e) if nm is not None else si.insert(0, e))
    d = r.find('defaults')
    if d is not None: r.remove(d)
    k = 40 / mm; H = 297 * k; W = 210 * k; mar = 12 * k
    d = etree.Element('defaults'); sc = etree.SubElement(d, 'scaling')
    etree.SubElement(sc, 'millimeters').text = str(mm); etree.SubElement(sc, 'tenths').text = '40'
    pl = etree.SubElement(d, 'page-layout'); etree.SubElement(pl, 'page-height').text = f'{H:.0f}'; etree.SubElement(pl, 'page-width').text = f'{W:.0f}'
    pm = etree.SubElement(pl, 'page-margins', type='both')
    for s in ('left', 'right', 'top', 'bottom'): etree.SubElement(pm, f'{s}-margin').text = f'{mar:.0f}'
    fc = r.find('credit')   # <defaults> must come before <credit>
    (fc.addprevious(d) if fc is not None else r.find('part-list').addprevious(d))
    pos = {'center': (W / 2, H - mar - 10), 'left': (mar, H - mar - 70), 'right': (W - mar, H - mar - 70)}
    for cw in r.iter('credit-words'):
        x, y = pos.get(cw.get('justify', 'center'), pos['center'])
        if cw.get('font-size') == '12': y -= 40     # subtitle under the title
        cw.set('default-x', f'{x:.0f}'); cw.set('default-y', f'{y:.0f}')
    for pr in r.iter('print'):   # notation programs paginate themselves; keep system breaks only
        if pr.get('new-page') == 'yes': del pr.attrib['new-page']; pr.set('new-system', 'yes')
    t.write(out, encoding='UTF-8', xml_declaration=True, pretty_print=True)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('xml'); ap.add_argument('outdir')
    ap.add_argument('--slug', required=True); ap.add_argument('--lang', default='en'); ap.add_argument('--workdir')
    A = ap.parse_args(); os.makedirs(A.outdir, exist_ok=True); i18 = load_i18n(A.lang)
    made = []
    for key, prog in PROGRAMS.items():
        xml = os.path.join(A.outdir, f'{A.slug}_{i18["sounds"][key]}.musicxml'); variant(A.xml, xml, prog); made.append(xml)
    for m in made: print('written:', m)
    if A.workdir: log_check(A.workdir, 4, 'make_scores', 'pass', f'{len(made)} files')

if __name__ == '__main__':
    main()
