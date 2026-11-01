#!/usr/bin/env python3
"""Logo set: the duck of the header image as white lines (a carved seal, "white characters") plus an eighth note on red ground.

  python3 site/logo/make_logo.py [--seed N] [--preview FILE]

1. Seal logo (only with --preview; no longer used, header and README show the smooth icon as docs/img/logo.png, 144 px): printed like the impression of a Chinese stone seal: nearly full-bleed red square with a slightly uneven edge,
   solid even red ink, small pin holes. The carved lines are opaque white (the paper), only the outside of the stone is transparent, so it looks the same
   on light and dark pages. Deterministic (fixed seed; --seed changes the texture).
2. Icons (favicon.svg, favicon-32.png, favicon.ico; app-icon-1024.png, favicon-180.png apple touch icon, favicon-192.png): one exact vector drawing,
   a flat red square to the very edge (no rounded corners: the operating system masks them), thick white lines, no texture, readable at 16 px.
   App icons keep more space around the drawing than the favicon (INSET).

--preview FILE writes a large preview of the seal logo. Needs numpy, scipy, pillow, cairosvg.
The duck comes from site/header/header-src.svg (group "duck"); the note is drawn once (note()) and used by both."""
import io, os, re, sys
import numpy as np
from PIL import Image
from scipy.ndimage import binary_dilation, binary_erosion, gaussian_filter, map_coordinates
import cairosvg

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..', '..'); IMG = os.path.join(ROOT, 'docs', 'img')
S = 2048                     # working size; 100 logo units = S px
RED = np.array([217, 37, 29], float)
SEED = int(sys.argv[sys.argv.index('--seed') + 1]) if '--seed' in sys.argv else 7
STROKE = 1.9                 # carved lines are this much thicker than in the header image
INSET = {'favicon': 0.92, 'app': 0.78}   # size of the drawing in the icon, 1 = as large as the bounding box allows
DUCK_SCALE, DUCK_X, DUCK_Y = 0.40, 29.0, 29.0   # duck: scale and position (logo units) of the duck's top left corner (x -2, y -62 in its own units)

def note(cx, cy, s, attrs):
    """Eighth note, head centre (cx, cy), scale s: slanted oval head, slim stem on its right side, a slim flag with a smooth curve."""
    return (f'<g transform="translate({cx} {cy}) scale({s})" {attrs}><ellipse rx="6" ry="4.4" transform="rotate(-22)"/>'
            '<path d="M3.9 -1.5V-24.5H7V-3Z"/><path d="M6.6 -24.6C7.6 -18.8 15.6 -18.4 14.9 -9.6C13.8 -13.6 11 -15.4 6.6 -16Z"/></g>')

def icon_parts():
    """The icon drawing in a 64 x 64 box (before centring and insetting): duck with thick white lines, note top left."""
    return ('<g transform="translate(17 33) scale(.30)" fill="#d9251d" stroke="#fff" stroke-width="12" stroke-linecap="round" stroke-linejoin="round">'
            '<path d="M14 6C8 -2 16 -10 24 -2C30 8 40 14 54 14C70 12 82 14 92 20L112 20C142 30 146 66 124 78C100 92 46 92 24 78C0 64 -2 30 14 6Z"/>'
            '<path d="M40 48C54 34 82 36 94 52" fill="none"/>'
            '<circle cx="98" cy="2" r="27"/><path d="M119 6C129 0 141 2 145 8C148 13 143 18 135 18C128 18 123 16 118 14Z"/></g>'
            '<circle cx="46.4" cy="32.6" r="2" fill="#fff"/>' + note(13, 25.5, .85, 'fill="#fff"'))

def icon_svg(inset):
    """Flat red square to the edge; the drawing is centred (measured) and scaled by inset."""
    body = icon_parts()
    png = cairosvg.svg2png(bytestring=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="640" height="640">{body}</svg>'.encode())
    a = np.asarray(Image.open(io.BytesIO(png)).convert('RGBA'))[..., 3]
    ys, xs = np.where(a > 8); x0, x1, y0, y1 = xs.min() / 10, (xs.max() + 1) / 10, ys.min() / 10, (ys.max() + 1) / 10
    k = inset * 64 / max(x1 - x0, y1 - y0)
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" fill="#d9251d"/>'
            f'<g transform="translate(32 32) scale({k:.4f}) translate({-(x0 + x1) / 2:.2f} {-(y0 + y1) / 2:.2f})">{body}</g></svg>\n')

def logo_svg(inset=0.80):
    """Header/README logo: the icon as a slightly rounded red tile, more space around the duck, and a thin red line around it (transparent gap in between)."""
    inner = icon_svg(inset).replace('<rect width="64" height="64" fill="#d9251d"/>', '<rect width="64" height="64" rx="9" fill="#d9251d"/>')
    inner = inner.replace('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">', '<svg x="5" y="5" width="54" height="54" viewBox="0 0 64 64">')
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
            '<rect x="1.2" y="1.2" width="61.6" height="61.6" rx="10" fill="none" stroke="#d9251d" stroke-width="2.4"/>' + inner + '</svg>')

def logo_png(size):
    png = cairosvg.svg2png(bytestring=logo_svg().encode(), output_width=size, output_height=size)
    return Image.open(io.BytesIO(png)).convert('RGBA')

def duck_mask_svg():
    src = open(os.path.join(ROOT, 'site', 'header', 'header-src.svg'), encoding='utf-8').read()
    duck = re.search(r'<g id="duck">(.*?)</g>', src, re.S).group(1)
    def thick(m):
        return f'stroke-width:{float(m.group(1)) * STROKE:.2f}'
    duck = re.sub(r'stroke-width:([\d.]+)', thick, duck)
    nt = note(22, 40, 1.4, 'class="d"')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{S}" height="{S}" viewBox="0 0 100 100"><rect width="100" height="100" fill="#000"/>'
            '<style>.k{fill:none;stroke:#fff;stroke-width:%.2f;stroke-linecap:round;stroke-linejoin:round}.w{fill:#000}.d{fill:#fff;stroke:none}.d *{fill:#fff;stroke:none}</style>' % (4.5 * STROKE)
            + f'<g transform="translate({DUCK_X + 2 * DUCK_SCALE:.2f} {DUCK_Y + 62 * DUCK_SCALE:.2f}) scale({DUCK_SCALE})">{duck}</g>{nt}</svg>')

def render_mask():
    png = cairosvg.svg2png(bytestring=duck_mask_svg().encode(), output_width=S, output_height=S)
    return np.asarray(Image.open(io.BytesIO(png)).convert('L'), float) / 255.0

def fbm(rng, cell, amp=1.0, octaves=1):
    """Smooth noise in [-1, 1] with the given cell size in px."""
    out = np.zeros((S, S), np.float32); a = 1.0; tot = 0
    for o in range(octaves):
        n = max(2, int(S / (cell / 2 ** o))) + 2
        small = rng.random((n, n), dtype=np.float32) * 2 - 1
        big = np.asarray(Image.fromarray(small, 'F').resize((S, S), Image.BICUBIC))
        out += a * big; tot += a; a *= 0.5
    return out / tot * amp

def rounded_square():
    y, x = np.mgrid[0:S, 0:S].astype(np.float32); m, r = 26, 40
    cx = np.clip(x, m + r, S - m - r); cy = np.clip(y, m + r, S - m - r)
    d = np.hypot(x - cx, y - cy)
    return (d <= r).astype(np.float32)

def build():
    rng = np.random.default_rng(SEED)
    carve = render_mask()
    # hand-carved wobble of the lines
    dx, dy = fbm(rng, 260, 9), fbm(rng, 260, 9)
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    carve = map_coordinates(carve, [yy + dy, xx + dx], order=1, mode='nearest')
    cb = gaussian_filter(carve, 5)
    edge = fbm(rng, 70, 0.22, 2) + fbm(rng, 16, 0.20, 2) + fbm(rng, 5, 0.09)
    carve2 = (cb + edge > 0.5).astype(np.float32)
    # the stone: rough, uneven edge and chipped corners
    sq = gaussian_filter(rounded_square(), 12)
    sq_edge = fbm(rng, 400, 0.16) + fbm(rng, 90, 0.12, 2) + fbm(rng, 20, 0.07) + fbm(rng, 5, 0.03)
    ground = (sq + sq_edge > 0.5)
    ground = (ground & binary_dilation(rounded_square() > 0.5, iterations=24)).astype(np.float32)   # no stray specks around the stone
    ground = gaussian_filter(ground, 1.0)
    # the ink: solid even red (no light clouds), small pin holes, a little darker towards the edge
    holes_n = fbm(rng, 9, 1.0, 2) * 0.6 + fbm(rng, 34, 1.0) * 0.4
    holes = np.clip((holes_n - 0.50) / 0.08, 0, 1)
    inner = gaussian_filter(binary_erosion(ground > 0.5, iterations=16).astype(np.float32), 6)   # pin holes only inside, the rim stays solid
    ink = (1 - carve2) * (1 - 0.92 * holes * inner)
    ink = gaussian_filter(ink, 0.9)
    rim = np.clip(ground - gaussian_filter(ground, 28), 0, 1)
    shade = 1 - 0.30 * rim
    red = np.clip(RED[None, None, :] * shade[..., None], 0, 255)
    paper = np.full_like(red, 255.0)                      # carved lines and pin holes are the white paper
    rgb = paper * (1 - ink[..., None]) + red * ink[..., None]
    rgb = rgb * ground[..., None] + RED[None, None, :] * (1 - ground[..., None])   # no white fringe where the stone ends
    out = np.dstack([rgb, np.clip(ground, 0, 1)[..., None] * 255]).astype(np.uint8)
    return Image.fromarray(out, 'RGBA')

def icon_png(inset, size):
    png = cairosvg.svg2png(bytestring=icon_svg(inset).encode(), output_width=size, output_height=size)
    return Image.open(io.BytesIO(png)).convert('RGB')

def main():
    if '--preview' in sys.argv:
        im = build(); bg = Image.new('RGBA', im.size, (255, 255, 255, 255))
        Image.alpha_composite(bg, im).convert('RGB').resize((1024, 1024), Image.LANCZOS).save(sys.argv[sys.argv.index('--preview') + 1]); return
    os.makedirs(IMG, exist_ok=True)
    logo_png(144).save(os.path.join(IMG, 'logo.png'), optimize=True)   # header and README: the icon with a thin outline and more space around the duck
    for n, f in ((1024, 'app-icon-1024.png'), (180, 'favicon-180.png'), (192, 'favicon-192.png')):
        icon_png(INSET['app'], n).save(os.path.join(IMG, f), optimize=True)
    open(os.path.join(IMG, 'favicon.svg'), 'w', encoding='utf-8').write(icon_svg(INSET['favicon']))
    icon_png(INSET['favicon'], 32).save(os.path.join(IMG, 'favicon-32.png'), optimize=True)
    icon_png(INSET['favicon'], 48).save(os.path.join(ROOT, 'docs', 'favicon.ico'), format='ICO', sizes=[(16, 16), (32, 32), (48, 48)])
    print('logo set written')

if __name__ == '__main__':
    main()
