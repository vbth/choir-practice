import io
import os
"""Shared helpers: i18n loading, file-name transliteration, check-log appending, date formats."""
import json, re, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
I18N_DIR = os.path.join(HERE, '..', 'assets', 'i18n')

def load_i18n(lang):
    p = os.path.join(I18N_DIR, f'{lang}.json')
    if not os.path.exists(p):
        raise SystemExit(f'No language pack for "{lang}". Create assets/i18n/{lang}.json by translating en.json '
                         f'(keep all keys), show it to the user, then rerun.')
    return json.load(open(p, encoding='utf-8'))

TRANS = {'ä': 'ae', 'ö': 'oe', 'ü': 'ue', 'Ä': 'Ae', 'Ö': 'Oe', 'Ü': 'Ue', 'ß': 'ss', 'é': 'e', 'è': 'e', 'à': 'a',
         'ç': 'c', 'ñ': 'n', 'ø': 'o', 'å': 'a', 'æ': 'ae', 'œ': 'oe'}

def safe(s):
    """File/folder-name safe: transliterate umlauts etc., spaces and hyphens -> _, drop other special chars."""
    s = ''.join(TRANS.get(c, c) for c in s)
    s = re.sub(r'[\s\-]+', '_', s.strip())     # spaces and hyphens become one underscore – names never contain a hyphen
    return re.sub(r'[^A-Za-z0-9_.]', '', s)

ACCENT = '#000000'   # no signal colour: table heads (bold) and the own voice in the overview (solid dot) are 100 % black like everything else

FOOT_PT = 8                      # footer size in pt on every PDF: identical everywhere (guides, logs, overview, score cover and music pages)
SEP = '\u00a0·\u00a0'              # one space before and after the middle dot

def footer_parts(lang, iso=None, kind='info'):
    """Footer as (text before the EU AI label, text after it): [label] + "YYYY-MM-DD KI-generiert. Nutzung auf eigene Gefahr." (no middle dot anywhere)."""
    note = load_i18n(lang)['ai_note' if kind == 'score' else 'ai_note_info']   # no middle dot anywhere: comma
    return '', f'{human_date(lang, iso)} {note}', kind

DASH = '\u2014'   # em dash: the separator of the footer, with a space on both sides

MD_LABEL = 'https://raw.githubusercontent.com/vbth/choir-practice/main/docs/img/'   # EU label for Markdown, linked from the repo (black, white in dark mode)

def md_footer(lang, title, iso=None):
    """Footer line of the Markdown files = the PDF footer: [EU label, linked from the repo] "YYYY-MM-DD KI-generiert. Nutzung auf eigene Gefahr." (no title),
    preceded and followed by one blank line (written by make_docs; the repo READMEs end the same way). Label height 18 px, proportional to ICON_H."""
    return (f'<a href="{SITE_URL}"><picture><source media="(prefers-color-scheme: dark)" srcset="{MD_LABEL}ai-basic-dark.svg">'
            f'<img src="{MD_LABEL}ai-basic.svg" alt="AI" height="18" align="absmiddle"></picture></a> '
            + f'{human_date(lang, iso)} ' + load_i18n(lang)['ai_meta'])

REPO_URL = 'https://github.com/vbth/choir-practice'   # the GitHub mark in the project line links here
SITE_URL = 'https://vbth.github.io/choir-practice/'   # the AI label in the footer links to the GitHub Pages site

def md_project(lang):
    """Project line of the Markdown files, one paragraph above the AI footer: [GitHub mark, linked to the repo] "choir-practice – KI-Musik-Workflow/-Skill für Claude."."""
    return (f'<a href="{REPO_URL}"><picture><source media="(prefers-color-scheme: dark)" srcset="{MD_LABEL}github-mark-dark.svg">'
            f'<img src="{MD_LABEL}github-mark.svg" alt="GitHub" height="18" align="absmiddle"></picture></a> ' + load_i18n(lang)['proj_note'].replace('-Skill', '-⁠Skill'))   # word joiner: no line break between "-" and "Skill"

def md_block(lang, title, iso=None):
    """Last two paragraphs of every Markdown file: project line, blank line, AI footer (md_footer)."""
    return md_project(lang) + '\n\n' + md_footer(lang, title, iso)

def footer_left(lang, iso=None, kind='info'):
    """Plain-text form of the footer (label left out)."""
    pre, note, _ = footer_parts(lang, iso, kind)
    return pre + note

def icon_path(kind):
    """EU label for every PDF footer: the basic label "AI" (no GENERATED / MODIFIED). The album art keeps "AI GENERATED" (make_cover.py)."""
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets', 'eu-ai-basic.svg')
# Footer rules (PDF and Markdown, checked by check_templates.py):
#   [EU label] <date> <ai_note_info>  - one line, flush left, no title, no middle dot; page number flush right where there is one
#   size FOOT_PT on every PDF; the label is sized so that the capitals of its letters (AI) are as high as the capitals
#   of the text and stand on the same baseline; Markdown: one blank line, md_footer(), one blank line (label linked from the repo)
PLEX_CAP = 0.698         # cap height of IBM Plex Sans in em
LABEL_WORD_CAP = 141 / 365.48   # cap height of the letters AI in the round label, in label heights
ICON_H = round(PLEX_CAP / LABEL_WORD_CAP, 3)   # label height in font sizes (1.809)
ICON_BASE = 0.6922   # baseline of the letters, from the top of the label, in label heights: label and text share one baseline

def _icon_vb(kind):
    import re
    raw = open(icon_path(kind), encoding='utf-8').read()
    return raw, [float(v) for v in re.search(r'viewBox="([^"]+)"', raw).group(1).split()]

def icon_width(font_size, kind='info'):
    """Width of the EU AI label when it is ICON_H × font size high (0 if the file is missing)."""
    if not os.path.exists(icon_path(kind)): return 0
    _, vb = _icon_vb(kind); return font_size * ICON_H * vb[2] / vb[3]

def icon_markup(x, y_baseline, font_size, kind='info'):
    """EU AI label as SVG group, ICON_H × font size high, the word in the label on the baseline of the text. '' if the file is missing."""
    if not os.path.exists(icon_path(kind)): return ''
    import re
    raw, vb = _icon_vb(kind); inner = re.search(r'<svg[^>]*>(.*)</svg>', raw, re.S).group(1)
    h = font_size * ICON_H; k = h / vb[3]
    return f'<g transform="translate({x:.2f},{y_baseline - h * ICON_BASE:.2f}) scale({k:.5f}) translate({-vb[0]},{-vb[1]})">{inner}</g>'

def gh_icon_markup(x, y_baseline, font_size, col_w):
    """GitHub mark as SVG group, exactly as high (diameter) as the AI label (ICON_H × font size) and on the same baseline relation, linked to the repo."""
    import re
    raw = open(os.path.join(os.path.dirname(icon_path('info')), 'github-mark.svg'), encoding='utf-8').read()
    inner = re.search(r'<svg[^>]*>(.*)</svg>', raw, re.S).group(1); h = font_size * ICON_H; k = h / 16
    return (f'<a href="{REPO_URL}"><g transform="translate({x + (col_w - h) / 2:.2f},{y_baseline - h * ICON_BASE:.2f}) scale({k:.5f})">{inner}</g></a>')

def icon_png(font_size, px_h=200, kind='info'):
    import cairosvg
    return cairosvg.svg2png(url=icon_path(kind), output_height=px_h) if os.path.exists(icon_path(kind)) else None

def text_width(txt, size, font='Times-Roman'):
    from reportlab.pdfbase import pdfmetrics
    return pdfmetrics.stringWidth(txt, font, size)

def today_iso():
    return datetime.date.today().isoformat()

def skill_version():
    """Version of the running skill (VERSION file next to scripts/)."""
    p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'VERSION')
    return open(p).read().strip() if os.path.exists(p) else 'unversioned'

def human_date(lang, iso=None):
    d = datetime.date.fromisoformat(iso or today_iso())
    return d.isoformat()   # ISO date (YYYY-MM-DD) in every language, German too

def log_check(workdir, phase, check, result, note=''):
    """Append one entry to <workdir>/checks.jsonl (result: pass | fail | warn | manual)."""
    os.makedirs(workdir, exist_ok=True)
    with open(os.path.join(workdir, 'checks.jsonl'), 'a', encoding='utf-8') as f:
        f.write(json.dumps({'time': datetime.datetime.now().isoformat(timespec='seconds'), 'phase': phase,
                            'check': check, 'result': result, 'note': note}, ensure_ascii=False) + '\n')

def read_checks(workdir):
    p = os.path.join(workdir, 'checks.jsonl')
    if not os.path.exists(p): return []
    return [json.loads(l) for l in open(p, encoding='utf-8') if l.strip()]


def repeat_endings(r):
    """Endings of one repeat as list of (passes, first_bar, last_bar). Entry forms: [a, b] (pass = its position) or
    {"passes": [1, 2], "bars": [a, b]} (one bracket for several passes, printed "1., 2.")."""
    out = []
    for k, e in enumerate(r.get('endings') or [], 1):
        if isinstance(e, dict): out.append((list(e['passes']), e['bars'][0], e['bars'][1]))
        else: out.append(([k], e[0], e[1]))
    return out

def repeat_times(r):
    ends = repeat_endings(r)
    return int(r.get('times') or max([2] + [p for ps, _, _ in ends for p in ps]))

def derive_playback(spec):
    """Ordered [first, last] measure ranges (1-based, pickup = 1) from spec['playback'] (explicit, wins) or from
    spec['repeats'] (any number of repeats, passes and endings); None = the score once as printed.
    Repeat: {"start": s, "end": e, "times": n} (section played n times, default 2) or
    {"start": s, "endings": [...], "times": n} with endings as in repeat_endings: pass p plays s..first ending-1
    and then the ending that lists p (no ending listed for p = none)."""
    if spec.get('playback'): return [tuple(x) for x in spec['playback']]
    reps = sorted(spec.get('repeats') or [], key=lambda r: r['start'])
    if not reps: return None
    n = len(spec['music'][spec['voices'][0]['id']]); out, i = [], 1
    for r in reps:
        s0 = r['start']
        if s0 > i: out.append((i, s0 - 1))
        ends = repeat_endings(r)
        if ends:
            first = min(a for _, a, _ in ends)
            for pas in range(1, repeat_times(r) + 1):
                if first > s0: out.append((s0, first - 1))
                for ps, a, b in ends:
                    if pas in ps: out.append((a, b))
            i = max(b for _, _, b in ends) + 1
        else:
            out += [(s0, r['end'])] * repeat_times(r); i = r['end'] + 1
    if i <= n: out.append((i, n))
    return out


PLEX_FILES = ('IBMPlexSans-Regular.ttf', 'IBMPlexSans-Bold.ttf', 'IBMPlexSans-Italic.ttf', 'IBMPlexSansCondensed-Regular.ttf', 'IBMPlexSansCondensed-Bold.ttf', 'IBMPlexSansCondensed-Italic.ttf')
PLEX_DIRS = ('/usr/share/fonts/truetype/ibm-plex', '~/.fonts/ibm-plex')   # apt package fonts-ibm-plex, or the fonts zip of the release (setup.sh)

def plex_dir():
    """Folder with the six IBM Plex Sans TTFs (system dependency, installed by setup.sh); both folders are scanned by fontconfig, so cairosvg finds them too."""
    for d in PLEX_DIRS:
        d = os.path.expanduser(d)
        if all(os.path.exists(os.path.join(d, fn)) for fn in PLEX_FILES): return d
    raise RuntimeError('IBM Plex Sans is not installed – run scripts/setup.sh (apt package fonts-ibm-plex or the fonts zip of the release)')

def register_plex():
    """IBM Plex Sans (SIL OFL, system font) for reportlab (PlexR / PlexB / PlexI)."""
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    d = plex_dir()
    for nm, fn in (('PlexR', 'IBMPlexSans-Regular.ttf'), ('PlexB', 'IBMPlexSans-Bold.ttf'), ('PlexI', 'IBMPlexSans-Italic.ttf')):
        if nm not in pdfmetrics.getRegisteredFontNames(): pdfmetrics.registerFont(TTFont(nm, os.path.join(d, fn)))

def rl_footer(c, left_x, right_x, y, size, page, title, lang, iso=None):
    """Footer of every PDF (reportlab), FOOT_PT on every PDF (`size` is ignored), IBM Plex Sans, 100 % black:
    flush left "[EU label AI GENERATED] YYYY-MM-DD KI-generiert. Nutzung auf eigene Gefahr." (no title), page number flush right (page=None: none, cover page).
    `title` is accepted for compatibility and not printed."""
    from reportlab.lib.utils import ImageReader
    register_plex()
    note = human_date(lang, iso) + ' ' + load_i18n(lang)['ai_note_info']
    def width(f): return icon_width(f, 'info') + f * 0.5 + text_width(note, f, 'PlexR') + (text_width(str(page), f, 'PlexR') + f * 3 if page else 0)
    size = FOOT_PT
    while width(size) > right_x - left_x and size > 6: size -= 0.25
    c.setFillColorRGB(0, 0, 0); c.setFont('PlexR', size)
    x = left_x
    png = icon_png(size, kind='info')
    if png:
        h = size * ICON_H; wd = icon_width(size, 'info'); c.drawImage(ImageReader(io.BytesIO(png)), x, y - h * (1 - ICON_BASE), wd, h, mask='auto')
        c.linkURL(SITE_URL, (x, y - h * (1 - ICON_BASE), x + wd, y + h * ICON_BASE), relative=0); x += wd + size * 0.5
    c.drawString(x, y, note)
    if page: c.drawRightString(right_x, y, str(page))
    # project line one line above: [GitHub mark, linked to the repo] choir-practice – KI-Musik-Workflow/-Skill für Claude.; the text starts in the same column as the AI note
    py = y + size * 1.9; col = icon_width(size, 'info'); pn = load_i18n(lang)['proj_note']
    gh = ImageReader(io.BytesIO(__import__('cairosvg').svg2png(url=os.path.join(os.path.dirname(icon_path('info')), 'github-mark.svg'), output_height=200)))
    g = size * ICON_H; c.drawImage(gh, left_x + (col - g) / 2, py - g * (1 - ICON_BASE), g, g, mask='auto')   # same diameter and baseline relation as the AI label
    c.linkURL(REPO_URL, (left_x, py - g * (1 - ICON_BASE), left_x + col, py + g * ICON_BASE), relative=0)
    ps = size
    while col + ps * 0.5 + text_width(pn, ps, 'PlexR') > right_x - left_x and ps > 6: ps -= 0.25   # long line: shrink instead of running off the page
    c.setFont('PlexR', ps); c.drawString(left_x + col + size * 0.5, py, pn)
