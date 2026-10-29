#!/usr/bin/env python3
"""One-page A4 landscape overview of the practice stages: for every voice and stage a headphone
diagram (own voice centred as a solid black dot, other voices as dots: position = left/right, size = level).

  python3 make_overview.py mixes.json score.json out.pdf [--png preview.png] [--workdir WORK]
"""
import json, sys, os, argparse
import cairosvg
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import load_i18n, log_check, ACCENT, icon_markup, icon_width, text_width, human_date, register_plex, FOOT_PT, gh_icon_markup
register_plex()   # Swiss design: IBM Plex Sans, flush left (20 mm margin), 100 % black, no fills, no colour

W, H = 1188, 840      # 4 px per mm
M = 80                # 20 mm margin
INK = '#000000'
FONT = 'font-family="IBM Plex Sans, sans-serif"'

def esc(s): return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('mixes'); ap.add_argument('spec'); ap.add_argument('out')
    ap.add_argument('--png'); ap.add_argument('--workdir')
    A = ap.parse_args()
    mx = json.load(open(A.mixes, encoding='utf-8')); spec = json.load(open(A.spec, encoding='utf-8'))
    i18 = load_i18n(spec.get('language', 'en')); O = i18['overview']
    seat = mx['seating']; names = mx['names']; N = len(seat)
    title = spec.get('meta', {}).get('title', '')
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><rect width="{W}" height="{H}" fill="white"/>']
    def T(x, y, s, size=13, w=400, a='start', c=INK):
        o.append(f'<text x="{x:.1f}" y="{y:.1f}" {FONT} font-size="{size}" font-weight="{w}" text-anchor="{a}" fill="{c}">{esc(s)}</text>')
    T(M, 104, O['title'].format(title=title), 24, 700)
    T(M, 128, O['sub1'], 12, 400)
    T(M, 146, O['sub2'].format(seating=' · '.join(names[v] for v in seat)), 12, 400)
    rows = ['solo', 'accomp', 'choir']; row_h = 195; y0 = 166
    pw = (W - 2 * M - (N - 1) * 10) / N
    mel = mx.get('melody'); mel_name = names.get(mel, '–') if mel else '–'
    for ri, st in enumerate(rows):
        ry = y0 + ri * row_h
        T(M, ry + 16, O['stage_titles'][st], 15, 700)
        sub_ = O['stage_subs'][st].format(melody=mel_name); sx_ = M + text_width(O['stage_titles'][st], 15, 'PlexB') + 28; fs_ = 12   # right after the title, shrunk if it would run off the page
        while sx_ + text_width(sub_, fs_, 'PlexR') > W - M and fs_ > 9: fs_ -= 0.5
        T(sx_, ry + 16, sub_, fs_, 400)
        for ci, own in enumerate(seat):
            x0 = M + ci * (pw + 10); py = ry + 26; ph = row_h - 36; cx = x0 + pw / 2; ay = py + ph * 0.52
            T(x0, py + 18, O['panel'].format(voice=names[own]), 12, 700, 'start')
            half = pw / 2 - 26
            o.append(f'<circle cx="{cx:.1f}" cy="{ay:.1f}" r="{min(46, half * 0.55):.1f}" fill="none" stroke="{INK}" stroke-width="0.75" stroke-dasharray="4 4"/>')
            for sx, lab in ((-1, 'L'), (1, 'R')):
                ex = cx + sx * (half + 8)
                o.append(f'<rect x="{ex - 10:.1f}" y="{ay - 24:.1f}" width="20" height="48" rx="8" fill="none" stroke="{INK}" stroke-width="1"/>')
                T(ex, ay + 5, lab, 13, 700, 'middle')
            o.append(f'<line x1="{cx - half:.1f}" y1="{ay:.1f}" x2="{cx + half:.1f}" y2="{ay:.1f}" stroke="{INK}" stroke-width="0.75"/>')
            entries = [e for e in mx['stages'][st][own] if not (e[0] == own and e[3] == 'own')]
            acc = [e for e in entries if e[3] == 'acc']; oth = [e for e in entries if e[3] != 'acc']
            if acc:   # accompaniment as a soft band
                o.append(f'<rect x="{cx - half * 0.55:.1f}" y="{ay + 30:.1f}" width="{half * 1.1:.1f}" height="12" rx="6" fill="none" stroke="{INK}" stroke-width="1"/>')
                T(cx, ay + 56, f"{O['accomp']} {acc[0][2]} dB", 10, 400, 'middle')
            for v, p, db, src in oth:
                r = max(5, 15 + db * 0.7); x = cx + p * (half - 22); y = ay - 34 if p == 0 else ay
                o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="white" stroke="{INK}" stroke-width="1.2"/>')
                T(x, y + 3.5, v, 8.5, 700, 'middle')
                T(x, (y - r - 4) if (p == 0 or abs(p) > 0.9) else (y + r + 12), f'{db}', 10, 400, 'middle')
            o.append(f'<circle cx="{cx:.1f}" cy="{ay:.1f}" r="15" fill="{ACCENT}"/>'); T(cx, ay + 4, own, 10, 700, 'middle', 'white')
    # footer (identical on every PDF): [EU label] AI note, date flush left, FOOT_PT (4 px per mm)
    lang = spec.get('language', 'en'); FS = FOOT_PT * 0.352778 * 4; dt = human_date(lang); note = i18['ai_note_info'] + ' ' + dt; yb = H - 46
    x = M
    o.append(icon_markup(x, yb, FS, 'info')); x += icon_width(FS, 'info') + FS * 0.5
    T(x, yb, note, FS)   # one page: no page number
    py = yb - FS * 1.9; col = icon_width(FS, 'info')   # project line one line above, text in the same column as the AI note
    o.append(gh_icon_markup(M, py, FS, col)); T(M + col + FS * 0.5, py, i18['proj_note'], FS)
    o.append('</svg>')
    svg = '\n'.join(o)
    cairosvg.svg2pdf(bytestring=svg.encode(), write_to=A.out, output_width=1123, output_height=794)
    if A.png: cairosvg.svg2png(bytestring=svg.encode(), write_to=A.png, output_width=1600, background_color='white')
    print('overview written:', A.out)
    if A.workdir: log_check(A.workdir, 6, 'make_overview', 'pass', 'one page A4 landscape')

if __name__ == '__main__':
    main()
