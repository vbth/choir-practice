#!/usr/bin/env python3
"""Album art for the MP3 files: one square cover per piece (the same for every voice), derived from the music.

  python3 make_cover.py score.json final.musicxml out.jpg [--workdir WORK]

Rules (all deterministic, so the same piece always gets the same cover):
  hue          key signature on the circle of fifths: 30 degrees per step, hue = 120 + 30 * fifths (mod 360); 12 steps close the colour
               circle, so enharmonic keys get the same colour (C major = green 120, G = 150, A = blue 210, F major = 90, 4 flats = red 0)
  register     mean pitch of all notes (MIDI): lightness of all four colour fields shifts by +-0.06 (middle C = 60 is neutral,
               +-12 semitones = full shift); high pieces come out lighter, low pieces darker
  mode         last note of the last part: tonic of the major key -> major (lighter, more saturated), tonic of the relative
               minor -> minor (darker, hue 12 degrees cooler, less saturated)
  softness     tempo in quarter notes per minute: slow = wide, soft radial transitions; fast = tighter, more contrast
  dark centre  metre: number of main beats per bar (6/8 = 2, 3/4 = 3, 4/4 = 4) moves the dark centre along the bottom edge
               (more beats = further left); the bottom right corner stays light for the EU label
EU label "AI" (round basic icon, black): fixed in the template (LABEL_H, LABEL_MARGIN): height 14 % of the cover, right and bottom margin 5 %
Exception: score.json may carry "cover": {"color": "#rrggbb"}; the hue then comes from that colour instead of the key (used for the example pack).
Four radial colour fields (light top left, saturated top right, mid bottom right, deep bottom centre) are blended, plus a little grain.
Legibility is guaranteed by construction and checked on the pixels: the title box (top left) and the label box (bottom right,
EU label "AI" alone, the black circle must stay recognisable) must both reach contrast >= 7:1 with black
(WCAG AAA). If the plain gradient is too dark there, a light feathered zone is blended in behind the boxes, step by step and
only as strong as needed. The text is always black, IBM Plex Sans, title bold; the EU label stands alone, no words next to it.
"""
import os, sys, json, colorsys, argparse, io
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from lxml import etree
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import log_check

HERE = os.path.dirname(os.path.abspath(__file__)); ASSETS = os.path.join(HERE, '..', 'assets')
SIZE = 600
LABEL_H = 0.14        # EU label "AI" (round): height as a fraction of the cover side (fixed in the template)
LABEL_MARGIN = 0.05   # distance of the label to the right and bottom edge, as a fraction of the cover side
REG_SHIFT = 0.06      # largest lightness shift from the register (mean pitch), +- this value at +-12 semitones from middle C
STEP = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}

def detect_minor(xml, fifths):
    """True if the piece ends on the tonic of the relative minor (last pitched note of the last part)."""
    try:
        r = etree.parse(xml).getroot(); last = None
        for n in r.findall('part')[-1].iter('note'):
            p = n.find('pitch')
            if p is not None: last = (STEP[p.findtext('step')] + int(float(p.findtext('alter') or 0))) % 12
        major = (fifths * 7) % 12
        return last is not None and last == (major + 9) % 12
    except Exception: return False

def mean_pitch(xml):
    """Mean pitch of all notes as a MIDI number (60 = middle C); 60 if nothing can be read."""
    try:
        v = [12 * (int(p.findtext('octave')) + 1) + STEP[p.findtext('step')] + int(float(p.findtext('alter') or 0)) for p in etree.parse(xml).getroot().iter('pitch')]
        return sum(v) / len(v) if v else 60.0
    except Exception: return 60.0

def qpm(tempo):
    """Tempo in quarter notes per minute from {'bpm', 'beat'}."""
    f = {'whole': 0.25, 'half': 0.5, 'quarter': 1, 'eighth': 2, 'dotted-half': 1 / 1.5, 'dotted-quarter': 1.5, 'dotted-eighth': 3}
    return float(tempo.get('bpm', 90)) * f.get((tempo.get('beat') or 'quarter').replace(' ', '-'), 1)

def beats_per_bar(ts):
    n, d = ts; return max(2, n // 3) if (d == 8 and n % 3 == 0 and n >= 6) else n

def lum(a):
    c = a / 255.0; c = np.where(c <= 0.03928, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    return 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]

# Generative album art: colours from key and mode, softness from tempo, a dark zone per beat in the bar
def render(hue, minor, soft, beats, zones=(), strength=0.0, seed=1, reg=0.0):
    S = SIZE; y, x = np.mgrid[0:S, 0:S] / (S - 1.0)
    dl, ds = (-0.08, -0.12) if minor else (0.0, 0.0); h = hue - (12 if minor else 0)
    def col(dh, l, s): return np.array(colorsys.hls_to_rgb(((h + dh) % 360) / 360.0, min(0.97, max(0.04, l + reg)), min(1, max(0, s)))) * 255
    dark_x = min(0.62, max(0.18, 0.50 - 0.07 * (beats - 2)))
    fields = [  # (centre x, centre y, colour)
        (0.05, 0.05, col(-6, 0.84, 0.70 + ds)),
        (0.97, 0.03, col(4, 0.62 + dl, 0.85 + ds)),
        (0.97, 0.97, col(2, 0.66 + dl, 0.80 + ds)),
        (dark_x, 0.92, col(-8, 0.11 if minor else 0.15, 0.60 + ds))]
    sig = soft; num = np.zeros((S, S, 3)); den = np.zeros((S, S))
    for cx, cy, c in fields:
        w = np.exp(-((x - cx) ** 2 + (y - cy) ** 2) / (2 * sig ** 2)); num += w[..., None] * c; den += w
    img = num / den[..., None]
    if strength > 0:   # light feathered zone behind the text boxes, only as strong as needed (legibility by construction)
        tint = col(-6, 0.90, 0.55); px = x * (S - 1); py = y * (S - 1)
        for (x0, y0, x1, y1) in zones:
            dx = np.maximum(np.maximum(x0 - px, px - x1), 0); dy = np.maximum(np.maximum(y0 - py, py - y1), 0)
            m = np.exp(-((dx ** 2 + dy ** 2) / (0.15 * S) ** 2)) * strength
            img = img * (1 - m[..., None]) + tint * m[..., None]
    rng = np.random.default_rng(seed); img += rng.normal(0, 1.2, img.shape)
    return np.clip(img, 0, 255).astype(np.uint8)

def title_layout(title, W, fnt_path):
    """Title lines (word wrap) and font size: big, at most 3 lines, within 80 % of the width."""
    for size in range(int(W * 0.13), int(W * 0.06), -2):
        f = ImageFont.truetype(fnt_path, size); words = title.split(); lines = []; cur = ''
        for w in words:
            t = (cur + ' ' + w).strip()
            if f.getlength(t) <= W * 0.80 or not cur: cur = t
            else: lines.append(cur); cur = w
        lines.append(cur)
        if len(lines) <= 3 and all(f.getlength(l) <= W * 0.80 for l in lines): return lines, f, size
    return lines, f, size

def make(spec, xml, out, workdir=None):
    S = SIZE; fifths = int(spec.get('key_fifths', 0)); minor = detect_minor(xml, fifths)
    hue = (120 + 30 * fifths) % 360
    col_hex = (spec.get('cover') or {}).get('color')   # optional override (the example pack uses the red of the website): hue taken from this colour
    if col_hex: hue = round(colorsys.rgb_to_hls(*(int(col_hex.lstrip('#')[i:i + 2], 16) / 255 for i in (0, 2, 4)))[0] * 360) % 360
    reg = REG_SHIFT * min(1.0, max(-1.0, (mean_pitch(xml) - 60) / 12.0)); q = qpm(spec.get('tempo') or {}); ts = spec.get('time') or [4, 4]
    soft = 0.36 - 0.14 * min(1.0, max(0.0, (q - 50) / 100.0)); beats = beats_per_bar(ts)
    title = spec['meta']['title']
    bold = os.path.join(ASSETS, 'fonts', 'IBMPlexSans-Bold.ttf')
    lines, ft, size = title_layout(title, S, bold); m = int(S * 0.075)
    tb = (m, m, int(m + max(ft.getlength(l) for l in lines)), int(m + size * 1.2 * len(lines)))   # title box
    ih = int(S * LABEL_H)
    import cairosvg
    svg = open(os.path.join(ASSETS, 'eu-ai-basic.svg'), encoding='utf-8').read()
    icon = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(), output_height=ih))).convert('RGBA')
    lb = int(S * LABEL_MARGIN); lx0, ly1 = S - lb - icon.width, S - lb; lb2 = (lx0, ly1 - ih, lx0 + icon.width, ly1)   # label box = the icon only (no text next to it): the black circle must stay recognisable
    pad = int(S * 0.02); zones = [(tb[0] - pad, tb[1] - pad, tb[2] + pad, tb[3] + pad), (lb2[0] - pad, lb2[1] - pad, lb2[2] + pad, lb2[3] + pad)]
    cbk = lambda L, b: (L[b[1]:b[3], b[0]:b[2]].min() + 0.05) / 0.05   # contrast with black = (L + 0.05) / 0.05, worst pixel = darkest
    for k in range(0, 11):
        strength = k / 10.0; arr = render(hue, minor, soft, beats, zones, strength, reg=reg); L = lum(arr.astype(float))
        res = (strength, cbk(L, tb), cbk(L, lb2))
        if res[1] >= 7 and res[2] >= 7: break
    ink = 'black'
    im = Image.fromarray(arr); d = ImageDraw.Draw(im); fg = (0, 0, 0) if ink == 'black' else (255, 255, 255)
    for i, l in enumerate(lines): d.text((m, m + i * size * 1.2), l, font=ft, fill=fg)
    ic = icon
    im.paste(ic, (lx0, ly1 - ih), ic)
    im.save(out, 'JPEG', quality=90, subsampling=0, optimize=True)
    ok = res[1] >= 7 and res[2] >= 7
    note = f'hue {hue}, register {reg:+.3f}, {"minor" if minor else "major"}, {q:.0f} quarter notes/min, {beats} main beats, title contrast {res[1]:.1f}:1, label contrast {res[2]:.1f}:1, light zone {res[0]:.1f}'
    if workdir: log_check(workdir, 5, 'cover_art', 'pass' if ok else 'fail', note)
    return ok, note

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('spec'); ap.add_argument('xml'); ap.add_argument('out'); ap.add_argument('--workdir')
    A = ap.parse_args(); ok, note = make(json.load(open(A.spec, encoding='utf-8')), A.xml, A.out, A.workdir); print(('OK ' if ok else 'FAIL ') + note); sys.exit(0 if ok else 1)
