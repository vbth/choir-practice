#!/usr/bin/env python3
"""Engrave the MusicXML as an A4 portrait PDF with Verovio – always readable, pages filled.

Layout rules
  * Readability is a hard limit: scale >= --min-scale (default 90 ≈ 1.6 mm staff space on A4).
    If no layout reaches it, more pages are allowed (up to --max-pages).
  * Not too much per page: systems whose text/notes would be squeezed are rejected
    (width estimate * scale <= DENSITY_MAX and no "highly compressed" warning from Verovio).
  * Every page filled vertically: equal number of systems per page, vertical justification.
  * Choice: fewest pages that satisfy all rules; tie -> largest scale.
  * Header line: title, credits, page number flush right; footer: date / AI note (lyrics font and size).

  python3 render_score.py score.musicxml out.pdf --lang de [--date 2026-01-31] [--min-scale 90]
        [--max-pages 6] [--force pages=2,spp=2] [--preview-dir DIR] [--write-xml final.musicxml] [--workdir WORK]

Writes out.layout.json and PNG previews (look at them!). With --workdir the result is logged.
"""
import sys, os, re, json, copy, argparse, io, tempfile, contextlib, subprocess
import verovio, cairosvg
import numpy as np
from PIL import Image
from lxml import etree
from xml.sax.saxutils import escape as esc
from pypdf import PdfReader, PdfWriter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import log_check, human_date, today_iso, icon_markup, icon_width, text_width, ACCENT, FOOT_PT, gh_icon_markup

DENSITY_MAX = 2950     # width estimate of widest system * scale; above this lyrics start to touch
BASE_W, BASE_H = 2100, 2970
MUSIC_FONT = os.environ.get('SCORE_MUSIC_FONT', 'Leland')   # notation font (Leipzig, Bravura, Gootville, Leland, Petaluma)
LINES = tuple(float(x) for x in os.environ.get('SCORE_LINES', '0.15,0.20,0.30').split(','))   # staff line, stem, barline width (Verovio units)
MARG = 200     # 20 mm top margin (1 unit = 0.1 mm on the A4 base page): room for the header line
HEAD_Y = 120   # header baseline 12 mm below the top edge
MARG_L = 200   # 20 mm left: the one text axis of every PDF (cover, footer, music, tables)
MARG_R = 200   # 20 mm right, like the other PDFs
FOOT_Y = 112   # footer baseline 11.2 mm above the page edge (label and descenders stay >= 10 mm), so nothing sits closer than 10 mm
GAP_MM = 6.5    # clear space (ink to ink) between page-1 title row, tempo line, first music, and before the footer line
BOTTOM = 270   # music ends 27 mm above the bottom: about 12 mm clear above the footer line

@contextlib.contextmanager
def capture_stderr():
    """Verovio writes warnings to the C stderr; capture them to detect over-compressed systems."""
    tmp = tempfile.TemporaryFile(mode='w+b'); fd = sys.stderr.fileno(); saved = os.dup(fd)
    sys.stderr.flush(); os.dup2(tmp.fileno(), fd)
    box = {}
    try:
        yield box
    finally:
        sys.stderr.flush(); os.dup2(saved, fd); os.close(saved)
        tmp.seek(0); box['text'] = tmp.read().decode('utf-8', 'replace'); tmp.close()

def measure_weights(root):
    """Width demand per bar (max over voices): per note max(text width, note width growing with duration) + bar overhead."""
    parts = root.findall('part'); n = len(parts[0].findall('measure'))
    div = int(root.find('.//divisions').text); eighth = div / 2
    w = [0.0] * n
    for p in parts:
        for i, m in enumerate(p.findall('measure')):
            tot = 0.8
            for ne in m.findall('note'):
                L = max([len(l.findtext('text') or '') for l in ne.findall('lyric')] + [0])
                d = int(ne.findtext('duration') or 0) / eighth
                tot += max(0.3 * L, 0.6 + 0.4 * d)
            w[i] = max(w[i], tot)
    return w

def partition(weights, S):
    """Split bars into S contiguous systems minimising the widest system (dynamic programming)."""
    n = len(weights)
    if S >= n: return list(range(n))
    pre = [0]
    for x in weights: pre.append(pre[-1] + x)
    INF = float('inf'); best = [[INF] * (n + 1) for _ in range(S + 1)]; cut = [[0] * (n + 1) for _ in range(S + 1)]
    best[0][0] = 0
    for k in range(1, S + 1):
        for j in range(k, n + 1):
            for i in range(k - 1, j):
                v = max(best[k - 1][i], pre[j] - pre[i])
                if v < best[k][j]: best[k][j] = v; cut[k][j] = i
    starts = []; j = n
    for k in range(S, 0, -1):
        i = cut[k][j]; starts.append(i); j = i
    return sorted(starts)

def with_breaks(root, starts, spp, pages=False):
    r = copy.deepcopy(root)
    for p in r.findall('part'):
        ms = p.findall('measure')
        for m in ms:
            for pr in m.findall('print'): m.remove(pr)
        for k, s in enumerate(starts):
            if s == 0: continue
            attrs = {'new-page': 'yes', 'new-system': 'yes'} if (pages and k % spp == 0) else {'new-system': 'yes'}
            ms[s].insert(0, etree.Element('print', **attrs))
    return etree.tostring(r, encoding='unicode')

def tk_for(xml, scale, mode='line'):
    f = 100 / scale; tk = verovio.toolkit()
    tk.setOptions({'pageWidth': int(BASE_W * f), 'pageHeight': int(BASE_H * f), 'scale': scale, 'adjustPageHeight': False,
                   'pageMarginLeft': int(MARG_L * f), 'pageMarginRight': int(MARG_R * f), 'pageMarginTop': int(MARG * f),
                   'pageMarginBottom': int(BOTTOM * f), 'header': 'none', 'footer': 'none', 'breaks': mode, 'font': MUSIC_FONT,
                   'justifyVertically': True, 'lyricSize': 3.8, 'staffLineWidth': LINES[0], 'stemWidth': LINES[1], 'lyricVerseCollapse': False, 'lyricTopMinMargin': 2.5, 'lyricLineThickness': 0.10, 'lyricHeightFactor': 1.3,
                   'spacingStaff': 14, 'spacingSystem': 18, 'spacingLinear': 0.4, 'barLineWidth': LINES[2]})
    tk.loadData(xml)
    return tk

def fill_of(svg):
    png = cairosvg.svg2png(bytestring=svg.encode(), output_width=600)
    im = Image.open(io.BytesIO(png)).convert('RGBA'); bg = Image.new('RGBA', im.size, 'white'); bg.alpha_composite(im)
    a = np.array(bg.convert('L')); rows = np.where((a < 128).sum(axis=1) > 0)[0]
    return float(rows.max() / a.shape[0]) if len(rows) else 0.0

def music_fill(svg):
    """Fill measured without the footer line (bottom 4 %)."""
    png = cairosvg.svg2png(bytestring=svg.encode(), output_width=600)
    im = Image.open(io.BytesIO(png)).convert('RGBA'); bg = Image.new('RGBA', im.size, 'white'); bg.alpha_composite(im)
    a = np.array(bg.convert('L')); a = a[:int(a.shape[0] * 0.955)]; rows = np.where((a < 128).sum(axis=1) > 0)[0]
    return float(rows.max() / (a.shape[0] / 0.955)) if len(rows) else 0.0

def enlarge_title(svg, title, subtitle=None):
    if not title: return svg
    m = re.search(r'<tspan font-size="(\d+)px">' + re.escape(title) + '</tspan>', svg)
    if not m: return svg
    new = int(int(m.group(1)) * 1.7)
    svg = svg.replace(m.group(0), f'<tspan font-size="{new}px">{title}</tspan>', 1)
    i = svg.find(f'<tspan font-size="{new}px">{title}</tspan>'); j = svg.rfind('class="rend"', 0, i)
    m2 = re.search(r'y="(\d+)"', svg[j:i])
    if m2:
        y = int(m2.group(1)); svg = svg[:j] + svg[j:i].replace(f'y="{y}"', f'y="{y + int(0.11 * new)}"', 1) + svg[i:]
    if subtitle:   # move the subtitle below the enlarged title
        k = svg.find('>' + subtitle + '</tspan>')
        if k > 0:
            j2 = svg.rfind('class="rend"', 0, k); m3 = re.search(r'y="(\d+)"', svg[j2:k])
            if m3:
                y2 = int(m3.group(1)); svg = svg[:j2] + svg[j2:k].replace(f'y="{y2}"', f'y="{y2 + int(0.5 * new)}"', 1) + svg[k:]
    return svg

def ink_bands(svg, px_w=1650):
    """Ink-covered row bands of the rendered page as (top_mm, bottom_mm) tuples, plus mm per pixel."""
    png = cairosvg.svg2png(bytestring=svg.encode(), output_width=px_w, background_color='white')
    a = np.array(Image.open(io.BytesIO(png)).convert('L')) < 140; mm = 297.0 / a.shape[0]
    rows = a.any(axis=1); runs = []; st = None
    for y, v in enumerate(rows):
        if v and st is None: st = y
        if not v and st is not None: runs.append((st * mm, (y - 1) * mm)); st = None
    if st is not None: runs.append((st * mm, (len(rows) - 1) * mm))
    return runs

def space_header(svg):
    """Page 1: the title row keeps >= 10 mm from the top edge, and title row -> tempo line -> first music each get GAP_MM of clear space
    (the same space the footer has below the music). The first system moves down, the tempo text moves back up relative to it."""
    runs = ink_bands(svg)
    if len(runs) < 3: return svg, None
    (t0, t1), (m0, m1), (s0, _) = runs[0], runs[1], runs[2]
    d_title = max(0.0, 10.0 - t0); t1 += d_title
    d_tempo = (t1 + GAP_MM) - m0; m1 += d_tempo
    d_music = (m1 + GAP_MM) - s0
    vb = re.search(r'<svg class="definition-scale"[^>]*viewBox="0 0 (\d+) (\d+)"', svg)
    u = int(vb.group(1)) / 210.0      # inner units per mm
    from lxml import etree as ET
    S = '{http://www.w3.org/2000/svg}'; root = ET.fromstring(svg.encode('utf-8'))
    pm = next(e for e in root.iter(S + 'g') if e.get('class') == 'page-margin')
    head = next((e for e in pm if (e.get('class') or '').startswith('pgHead')), None)
    systems = [e for e in pm if e.get('class') == 'system']
    if head is None or not systems: return svg, None
    dr = next((e for e in systems[0].iter(S + 'g') if (e.get('class') or '').startswith('dir')), None)
    head.set('transform', f'translate(0,{d_title * u:.1f})')
    systems[0].set('transform', f'translate(0,{d_music * u:.1f})')
    if dr is not None: dr.set('transform', f'translate(0,{(d_tempo - d_music) * u:.1f})')
    return ET.tostring(root, encoding='unicode'), {'title_down_mm': round(d_title, 1), 'first_system_down_mm': round(d_music, 1)}

def header_parts(spec, root, lang):
    """Header text of the music pages: (title, rest) = "Title" bold, ", Name(s) (Text), Name(s) (Musik)" regular; names comma separated."""
    from common import load_i18n
    C = load_i18n(lang)['cover']; m = spec.get('meta', {})
    title = m.get('title') or root.findtext('work/work-title') or ''
    cr = {(c.get('type') or ''): (c.text or '') for c in root.iter('creator')}
    def names(v):
        v = v or ''
        return ', '.join(str(x).strip() for x in v) if isinstance(v, (list, tuple)) else str(v).strip()
    rest = ''
    for key, fallback in (('lyricist', 'lyricist'), ('composer', 'composer')):
        n = names(m.get(key) or cr.get(fallback))
        if n: rest += f', {n} ({C[key]})'
    return title, rest

def add_header(svg, title, rest, page=None):
    """Header of the music pages: one line flush left on the 20 mm axis, title bold, same size as the lyrics, IBM Plex Sans;
    the page number sits flush right on the same line (where the eye is when turning pages)."""
    vb = re.search(r'(<svg class="definition-scale"[^>]*viewBox="0 0 (\d+) (\d+)"[^>]*>)', svg)
    syl = re.search(r'class="syl".*?<tspan font-size="(\d+)px"', svg, re.S)
    if not vb or not title: return svg
    VW, VH = int(vb.group(2)), int(vb.group(3))
    fs = int(syl.group(1)) if syl else int(12 * 0.352778 * VW / 210)
    y = int(VH * HEAD_Y / BASE_H); xl = int(VW * MARG_L / BASE_W); xr = VW - int(VW * MARG_R / BASE_W)
    pw = lambda f: (text_width(str(page), f, 'PlexR') + f * 3) if page else 0
    while text_width(title, fs, 'PlexB') + text_width(rest, fs, 'PlexR') + pw(fs) > xr - xl and fs > 6: fs -= 1
    txt = (f'<text x="{xl}" y="{y}" font-family="{FONT_NAME}, sans-serif" font-size="0px" text-anchor="start" xml:space="preserve"><tspan class="text">'
           f'<tspan font-size="{fs}px" font-weight="bold">{esc(title)}</tspan><tspan font-size="{fs}px">{esc(rest)}</tspan></tspan></text>')
    if page: txt += (f'<text x="{xr}" y="{y}" font-family="{FONT_NAME}, sans-serif" font-size="0px" text-anchor="end" xml:space="preserve"><tspan class="text"><tspan font-size="{fs}px">{page}</tspan></tspan></text>')
    k = svg.rfind('</svg>', 0, svg.rfind('</svg>'))
    return svg[:k] + txt + svg[k:]

def add_footer(svg, lang, iso):
    """Footer of the music pages: flush left "[EU label] KI-generiert. Urheber- und Lizenzrechte beachten. Nutzung auf eigene Gefahr. YYYY-MM-DD" (the page number is in the header here),
    FOOT_PT like every PDF footer, IBM Plex Sans. Placed inside Verovio's inner scaled SVG, aligned with the music margins."""
    vb = re.search(r'(<svg class="definition-scale"[^>]*viewBox="0 0 (\d+) (\d+)"[^>]*>)', svg)
    if not vb: return svg
    from common import load_i18n
    VW, VH = int(vb.group(2)), int(vb.group(3))
    fs = int(round(FOOT_PT * 0.352778 * VW / 210))   # FOOT_PT, like every PDF footer
    y = int(VH - VH * FOOT_Y / BASE_H); xl = int(VW * MARG_L / BASE_W); xr = VW - int(VW * MARG_R / BASE_W)
    note = load_i18n(lang)['ai_note_info'] + ' ' + human_date(lang, iso)
    def width(f): return icon_width(f, 'info') + f * 0.5 + text_width(note, f, 'PlexR') + f * 3
    while width(fs) > (xr - xl) and fs > 6: fs -= 1   # long titles: shrink instead of colliding
    def t(x, anchor, txt, y=y):
        return (f'<text x="{x}" y="{y}" font-family="{FONT_NAME}, sans-serif" font-size="0px" text-anchor="{anchor}" xml:space="preserve"><tspan class="text"><tspan font-size="{fs}px">{txt}</tspan></tspan></text>')
    x = xl
    out = icon_markup(x, y, fs, 'info'); x += icon_width(fs, 'info') + fs * 0.5
    out += t(x, 'start', note)
    py = int(y - fs * 1.9); col = icon_width(fs, 'info'); pn = load_i18n(lang)['proj_note']   # project line one line above, same text column
    out += gh_icon_markup(xl, py, fs, col) + t(xl + col + fs * 0.5, 'start', pn, py)
    k = svg.rfind('</svg>', 0, svg.rfind('</svg>'))   # closing tag of the inner svg
    return svg[:k] + out + svg[k:]

def highlight_part(svg, k, nparts, tint='#FFF1B8'):
    """Highlight part k (0-based) in every system: tinted band behind its staves and lyrics, label bold in the accent colour.
    The text stays black, so the page also prints well in black and white."""
    from lxml import etree as ET
    NS = '{http://www.w3.org/2000/svg}'
    root = ET.fromstring(svg.encode('utf-8')); cls = lambda e: (e.get('class') or '').split()
    def kids(e, c): return [x for x in e if x.tag == NS + 'g' and c in cls(x)]
    for system in root.iter(NS + 'g'):
        if 'system' not in cls(system): continue
        labels = kids(system, 'label') or kids(system, 'labelAbbr')
        if len(labels) >= nparts:
            for t in labels[k].iter(NS + 'tspan'):
                if t.get('font-size'): t.set('font-weight', 'bold'); t.set('fill', ACCENT)
        boxes = []
        for measure in kids(system, 'measure'):
            staves = kids(measure, 'staff')
            if len(staves) <= k: continue
            st = staves[k]; ys, xs = [], []
            for pth in st:
                if pth.tag == NS + 'path' and pth.get('d', '').startswith('M') and ' L' in pth.get('d', ''):
                    m = re.match(r'M(-?\d+) (-?\d+) L(-?\d+) (-?\d+)', pth.get('d'))
                    if m and m.group(2) == m.group(4): xs += [int(m.group(1)), int(m.group(3))]; ys.append(int(m.group(2)))
            if len(ys) < 5: continue
            top, bot = min(ys), max(ys); sp = (bot - top) / 4; low = int(bot + 0.4 * sp)
            for t in st.iter(NS + 'text'):
                if t.get('y') and t.get('y').lstrip('-').isdigit():
                    sizes = [int(x.get('font-size', '0px')[:-2] or 0) for x in t.iter(NS + 'tspan') if (x.get('font-size') or '0px').endswith('px')]
                    f = max(sizes) if sizes else 0
                    if int(t.get('y')) > bot and f: low = max(low, int(t.get('y')) + int(0.3 * f))
            boxes.append((measure, st, min(xs), max(xs), int(top - 1.3 * sp), low))
        if not boxes: continue
        low = max(b[5] for b in boxes)   # same bottom edge for every bar of the system
        for measure, st, x1, x2, y1, _ in boxes:
            rect = ET.Element(NS + 'rect', x=str(x1), y=str(y1), width=str(x2 - x1), height=str(low - y1), fill=tint)
            measure.insert(list(measure).index(st), rect)
    return ET.tostring(root, encoding='unicode')

def strip_header_pagenum(svg):
    """Verovio's auto header prints '– n –' at the top of pages ≥ 2; the number belongs at the bottom."""
    return re.sub(r'<tspan font-size="\d+px">–\s*\d+\s*–</tspan>', '', svg)


FONT_NOTES = 'IBM Plex Sans Condensed'   # lyrics, tempo word, bar numbers: the condensed cut of the same family (width 85) – Verovio plans the syllable spacing with narrow text, regular width made syllables collide
FONT_NAME = 'IBM Plex Sans'   # cover page and footer of every PDF; the notation (Leland) and the lyrics keep Verovio's own fonts

def ensure_fonts():
    from common import register_plex
    register_plex()

def make_cover(spec, root, lang, iso, locate=None):
    """Cover page template (Swiss style, always identical): everything flush left on the 20 mm axis, IBM Plex Sans, 100 % black,
    no rules: the title in bold, below it Musik / Text as label/value grid; at the bottom the same footer as every PDF (without page number)."""
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from common import load_i18n, rl_footer
    ensure_fonts(); R_, B_ = 'PlexR', 'PlexB'
    i = load_i18n(lang); C = i['cover']; m = spec.get('meta', {})
    title = m.get('title') or root.findtext('work/work-title') or ''
    cr = {(c.get('type') or ''): (c.text or '') for c in root.iter('creator')}
    rows = [(C['lyricist'], m.get('lyricist') or cr.get('lyricist')), (C['composer'], m.get('composer') or cr.get('composer'))]   # Text, Musik – the order of the header line
    mm = 2.835; W, H = 595.28, 841.89; X = 20 * mm; XV = X + 22 * mm; BODY = 12
    buf = io.BytesIO(); c = canvas.Canvas(buf, pagesize=(W, H)); c.setTitle(title); c.setFillColorRGB(0, 0, 0)
    size = 30; TRACK = -0.015   # display size: tracking slightly tighter (in em), body text keeps the font's own spacing
    tw = lambda s: pdfmetrics.stringWidth(title, B_, s) + TRACK * s * max(0, len(title) - 1)
    while size > 18 and tw(size) > W - 2 * X: size -= 1
    tx = c.beginText(X, H - 96 * mm); tx.setFont(B_, size); tx.setCharSpace(TRACK * size); tx.textOut(title); c.drawText(tx)
    y = H - 118 * mm; c.setFont(R_, BODY)
    for r in rows:
        if r[1]: c.drawString(X, y, r[0]); c.drawString(XV, y, r[1]); y -= 19
    # printed execution remarks of the source (performance_notes): text, and where to find the place in the score (bar and page)
    from reportlab.lib.utils import simpleSplit
    notes = [(n, None) if isinstance(n, str) else (n['text'], n.get('bar')) for n in spec.get('performance_notes') or []]
    if notes:
        XN = X + 38 * mm; y -= 14; c.setFont(B_, BODY); c.drawString(X, y, C['notes_h']); y -= 19; c.setFont(R_, BODY)
        for text, bar in notes:
            ref = C['bar_page'].format(bar=bar, page=locate(bar)) if bar is not None and locate else ''
            for k, line in enumerate(simpleSplit(text, R_, BODY, W - X - XN)):
                if k == 0 and ref: c.drawString(X, y, ref)
                c.drawString(XN, y, line); y -= 16
            y -= 3
    rl_footer(c, X, W - X, 12 * mm, BODY, None, title, lang, iso)
    c.showPage(); c.save(); return buf.getvalue()

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('xml'); ap.add_argument('pdf')
    ap.add_argument('--lang', default='en'); ap.add_argument('--date'); ap.add_argument('--spec', help='score.json: metadata for the cover page')
    ap.add_argument('--min-scale', type=int, default=90); ap.add_argument('--max-pages', type=int, default=6)
    ap.add_argument('--force'); ap.add_argument('--highlight', type=int, help='1-based part number to highlight (own-voice score); no layout file, no log'); ap.add_argument('--preview-dir'); ap.add_argument('--write-xml'); ap.add_argument('--workdir')
    A = ap.parse_args()
    ensure_fonts()
    root = etree.parse(A.xml).getroot()
    for sp in root.iter('score-part'):   # first system shows the abbreviation too (T1, B2 …) – the full names stay in the delivered MusicXML/MuseScore files
        ab, nm = sp.find('part-abbreviation'), sp.find('part-name')
        if ab is not None and nm is not None and ab.text: nm.text = ab.text
    w = measure_weights(root); n = len(w)
    off = 1 if (root.find('part/measure').get('implicit') == 'yes' and n > 1) else 0
    w2 = [w[0] + w[1]] + w[2:] if off else w
    forced = dict(x.split('=') for x in A.force.split(',')) if A.force else None
    cands = []
    for P in range(1, A.max_pages + 1):
        for spp in range(1, 6):
            if forced and (P != int(forced['pages']) or spp != int(forced['spp'])): continue
            S = P * spp
            if S > len(w2): continue
            st = partition(w2, S); starts = ([0] + [s + off for s in st[1:]]) if off else st
            groups = [sum(w[starts[k]:(starts[k + 1] if k + 1 < len(starts) else n)]) for k in range(len(starts))]
            xml = with_breaks(root, starts, spp)
            lo, hi, best, per = 30, 160, None, []
            with capture_stderr():
                while lo <= hi:
                    mid = (lo + hi) // 2
                    if tk_for(xml, mid).getPageCount() <= P: best = mid; lo = mid + 1
                    else: hi = mid - 1
                if best is not None:
                    tk = tk_for(xml, best)
                    if tk.getPageCount() == P:
                        per = [tk.renderToSVG(pg).count('class="system"') for pg in range(1, P + 1)]
            if best is None or per != [spp] * P: continue
            sc = min(best, int(DENSITY_MAX / max(groups)))
            cands.append({'pages': P, 'spp': spp, 'scale': sc, 'fit_scale': best, 'starts': starts,
                          'density': round(max(groups) * sc), 'xml': with_breaks(root, starts, spp, pages=True)})
        if not forced and any(c['scale'] >= A.min_scale for c in cands): break   # fewest pages reached
    if not cands: sys.exit('No layout found – raise --max-pages')
    readable = [c for c in cands if c['scale'] >= A.min_scale]
    order = sorted(readable, key=lambda c: (c['pages'], -c['scale'])) or sorted(cands, key=lambda c: -c['scale'])
    pick = None
    for c in order:   # final check: no over-compressed systems
        with capture_stderr() as box:
            tk = tk_for(c['xml'], c['scale'], mode='encoded'); [tk.renderToSVG(pg) for pg in range(1, tk.getPageCount() + 1)]
        if 'highly compressed' in box.get('text', ''):
            c['compressed'] = True; continue
        pick = c; break
    if pick is None: pick = order[0]; pick['compressed'] = True
    with capture_stderr():
        tk = tk_for(pick['xml'], pick['scale'], mode='encoded')
        svgs = [tk.renderToSVG(pg) for pg in range(1, tk.getPageCount() + 1)]
    out = PdfWriter(); fills = []
    spec = json.load(open(A.spec, encoding='utf-8')) if A.spec else {}
    nums = [m.get('number') for m in root.find('part').findall('measure')]
    def locate(bar):
        """Page of the PDF (cover = 1) that holds measure number `bar`."""
        if str(bar) not in nums: sys.exit(f'performance_notes: bar {bar} not found (measure numbers: {nums[0]}..{nums[-1]})')
        k = max(j for j, s in enumerate(pick['starts']) if s <= nums.index(str(bar)))
        return k // pick['spp'] + 2
    out.add_page(PdfReader(io.BytesIO(make_cover(spec, root, A.lang, A.date or today_iso(), locate))).pages[0])
    pv = A.preview_dir or os.path.dirname(os.path.abspath(A.pdf)); os.makedirs(pv, exist_ok=True)
    base = os.path.splitext(os.path.basename(A.pdf))[0]; previews = []
    for pg, svg in enumerate(svgs, 1):
        svg = svg.replace('font-family="Times, serif"', f'font-family="{FONT_NOTES}, sans-serif"')   # sans-serif lyrics
        svg = add_header(add_footer(strip_header_pagenum(svg), A.lang, A.date or today_iso()), *header_parts(spec, root, A.lang), page=pg + 1)   # the cover page is page 1 (unnumbered)
        if A.highlight: svg = highlight_part(svg, A.highlight - 1, len(root.findall('part')))
        fills.append(round(music_fill(svg), 3))
        out.add_page(PdfReader(io.BytesIO(cairosvg.svg2pdf(bytestring=svg.encode(), output_width=794, output_height=1123))).pages[0])
        im = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(), output_width=1400))).convert('RGBA')
        bgi = Image.new('RGBA', im.size, 'white'); bgi.alpha_composite(im)
        pth = os.path.join(pv, f'{base}_p{pg}.png'); bgi.convert('RGB').save(pth); previews.append(pth)
    out.write(A.pdf)
    cov = os.path.join(pv, f'{base}_p0_cover'); subprocess.run(['pdftoppm', '-r', '70', '-f', '1', '-l', '1', '-png', '-singlefile', A.pdf, cov], check=False); previews.insert(0, cov + '.png')
    if A.write_xml: open(A.write_xml, 'w', encoding='utf-8').write('<?xml version="1.0" encoding="UTF-8"?>\n' + pick['xml'])
    lay = {'cover': True, 'pages': pick['pages'], 'systems_per_page': pick['spp'], 'scale': pick['scale'], 'min_scale': A.min_scale,
           'staff_space_mm': round(1.8 * pick['scale'] / 100, 2), 'system_starts': pick['starts'], 'page_fill': fills,
           'density': pick['density'], 'compressed': pick.get('compressed', False), 'previews': previews,
           'candidates': [{k: c.get(k) for k in ('pages', 'spp', 'scale', 'fit_scale', 'density', 'compressed')} for c in cands]}
    if A.highlight:
        print(f'highlighted part {A.highlight}: {A.pdf}'); return
    json.dump(lay, open(os.path.splitext(A.pdf)[0] + '.layout.json', 'w'), indent=1)
    ok = pick['scale'] >= A.min_scale and min(fills) >= 0.8 and not lay['compressed']
    print(f"PDF {A.pdf}: {lay['pages']} page(s), {pick['spp']} systems/page, scale {pick['scale']} "
          f"(staff space {lay['staff_space_mm']} mm), fill {fills}, compressed={lay['compressed']}")
    print('system starts (bar index):', pick['starts']); print('previews:', ', '.join(previews))
    if not ok: print('ATTENTION: readability/fill rule not met – inspect previews, consider --force or more pages')
    if A.workdir:
        log_check(A.workdir, 4, 'render_score', 'pass' if ok else 'fail',
                  f"{lay['pages']} pages, scale {pick['scale']} (min {A.min_scale}), staff space {lay['staff_space_mm']} mm, fill {fills}, compressed={lay['compressed']}")

if __name__ == '__main__':
    main()
