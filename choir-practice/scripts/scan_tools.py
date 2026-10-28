#!/usr/bin/env python3
"""Helpers for reading a score from a PDF (scan or export).

  topdf   <image>... <out.pdf>           photos / scans as images (JPG, PNG, TIFF, WebP; one image per page, in the given order) -> one PDF
  extract <pdf> <outdir>                 pages as PNG (300 dpi) + text layer (if any)
  staves  <page.png> [--out staves.json] detect staff lines -> staves with y positions
  crops   <page.png> <staves.json> <outdir> [--per-system K] [--segments 3] [--zoom 2.6] [--guides]
                                          crops per system and segment (staves stacked, lyrics left out)
                                          plus one full crop per system with lyrics (for syllable alignment)

Look at the crops with the Read tool. --guides labels lines/spaces with sounding pitch names
(treble8 = tenor clef, bass) – useful for dense chords.
"""
import sys, os, json, subprocess, argparse
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def extract(pdf, outdir):
    os.makedirs(outdir, exist_ok=True)
    subprocess.run(['pdftoppm', '-r', '300', '-png', pdf, os.path.join(outdir, 'page')], check=True)
    txt = subprocess.run(['pdftotext', '-layout', pdf, '-'], capture_output=True, text=True).stdout
    open(os.path.join(outdir, 'textlayer.txt'), 'w').write(txt)
    info = subprocess.run(['pdfinfo', pdf], capture_output=True, text=True).stdout
    imgs = subprocess.run(['pdfimages', '-list', pdf], capture_output=True, text=True).stdout
    pages = sorted(f for f in os.listdir(outdir) if f.startswith('page') and f.endswith('.png'))
    print(info.strip()); print('images in PDF:\n' + imgs.strip())
    print('pages:', pages)
    print('text layer:', len(txt.strip()), 'chars ->', os.path.join(outdir, 'textlayer.txt'))
    print('note: if the PDF is a scan (one large image per page) the text layer is OCR and unreliable.')

def topdf(images, out):
    """One PDF from one or more image files (photo or scan of the score). EXIF rotation is applied; the pixels stay untouched (no resampling)."""
    from PIL import ImageOps
    pages = [ImageOps.exif_transpose(Image.open(p)).convert('RGB') for p in images]
    pages[0].save(out, 'PDF', save_all=True, append_images=pages[1:], resolution=300.0)
    print(f'{len(pages)} page(s) -> {out}')

def _dark(path, thr=110):
    g = np.array(Image.open(path).convert('L')).astype(int)
    return g < thr, g.shape

def _groups(rows, gap=2):
    out, cur = [], []
    for r in rows:
        if cur and r - cur[-1] > gap:
            out.append(cur); cur = []
        cur.append(r)
    if cur: out.append(cur)
    return [sum(c) / len(c) for c in out]

def staves(page, out=None):
    dark, (H, W) = _dark(page)
    # several vertical strips so that slightly rotated photos still work
    xs = [int(W * f) for f in (0.25, 0.5, 0.75)]
    cand = []
    for x in xs:
        prof = dark[:, x:x + int(W * 0.08)].sum(axis=1)
        rows = [i for i, v in enumerate(prof) if v > 0.6 * int(W * 0.08)]
        cand.append(_groups(rows))
    lines = sorted(cand[1])
    # build groups of 5 evenly spaced lines
    staffs, i = [], 0
    while i + 4 < len(lines):
        grp = lines[i:i + 5]
        d = np.diff(grp)
        if d.max() - d.min() <= max(3, 0.25 * d.mean()) and 5 < d.mean() < H / 40:
            staffs.append({'lines': [round(v, 1) for v in grp], 'space': round(float(d.mean()), 2),
                           'top': round(grp[0], 1), 'bottom': round(grp[-1], 1)})
            i += 5
        else:
            i += 1
    res = {'page': page, 'width': W, 'height': H, 'staves': staffs}
    js = json.dumps(res, indent=1)
    if out: open(out, 'w').write(js)
    print(f'{len(staffs)} staves detected')
    for k, s in enumerate(staffs):
        print(f"  staff {k}: y {s['top']}-{s['bottom']}  line spacing {s['space']}")
    return res

TREBLE8 = ['C3', 'D3', 'E3', 'F3', 'G3', 'A3', 'B3', 'C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'B4', 'C5']  # index 2 = bottom line
TREBLE = [p[0] + str(int(p[1]) + 1) for p in TREBLE8]
BASS = ['E2', 'F2', 'G2', 'A2', 'B2', 'C3', 'D3', 'E3', 'F3', 'G3', 'A3', 'B3', 'C4', 'D4', 'E4']

def crops(page, staves_json, outdir, per_system=2, segments=3, zoom=2.6, guides=False, clefs=None):
    os.makedirs(outdir, exist_ok=True)
    S = json.load(open(staves_json))
    im = Image.open(page).convert('RGB'); W, H = im.size
    st = S['staves']
    systems = [st[i:i + per_system] for i in range(0, len(st), per_system)]
    try:
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 14)
    except Exception:
        font = ImageFont.load_default()
    edges = np.linspace(0, W, segments + 1).astype(int)
    ov = int(W * 0.04)
    made = []
    for si, sysst in enumerate(systems):
        # full crop with lyrics
        top = int(sysst[0]['top'] - 6 * sysst[0]['space']); bot = int(sysst[-1]['bottom'] + 7 * sysst[-1]['space'])
        full = im.crop((0, max(0, top), W, min(H, bot)))
        p = os.path.join(outdir, f'{os.path.basename(page)[:-4]}_sys{si+1}_full.png'); full.save(p); made.append(p)
        for j in range(segments):
            xa, xb = max(0, edges[j] - ov), min(W, edges[j + 1] + ov)
            parts = []
            for k, s in enumerate(sysst):
                sp = s['space']; y0 = int(s['top'] - 4.5 * sp); y1 = int(s['bottom'] + 4.5 * sp)
                c = im.crop((xa, max(0, y0), xb, min(H, y1))).resize((int((xb - xa) * zoom), int((min(H, y1) - max(0, y0)) * zoom)), Image.LANCZOS)
                if guides:
                    d = ImageDraw.Draw(c)
                    names = (clefs[k] if clefs and k < len(clefs) else ('bass' if k % 2 else 'treble8'))
                    names = {'treble8': TREBLE8, 'treble': TREBLE, 'bass': BASS}[names]
                    for idx, nm in enumerate(names):
                        y = (s['bottom'] - (idx - 2) * sp / 2 - max(0, y0)) * zoom
                        col = (210, 0, 0) if idx % 2 == 0 else (0, 110, 230)
                        for x in range(60, c.width, 16): d.line([(x, y), (x + 5, y)], fill=col, width=1)
                        d.text((4, y - 8), nm, fill=col, font=font)
                parts.append(c)
            h = sum(c.height for c in parts) + 8 * (len(parts) - 1)
            out = Image.new('RGB', (parts[0].width, h), 'white'); y = 0
            for c in parts:
                out.paste(c, (0, y)); y += c.height + 8
            p = os.path.join(outdir, f'{os.path.basename(page)[:-4]}_sys{si+1}_seg{j+1}.png'); out.save(p); made.append(p)
    print('\n'.join(made))

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest='cmd')
    t = sub.add_parser('topdf'); t.add_argument('files', nargs='+', help='image files ... out.pdf (the last argument is the PDF)')
    a = sub.add_parser('extract'); a.add_argument('pdf'); a.add_argument('outdir')
    b = sub.add_parser('staves'); b.add_argument('page'); b.add_argument('--out')
    c = sub.add_parser('crops'); c.add_argument('page'); c.add_argument('staves'); c.add_argument('outdir')
    c.add_argument('--per-system', type=int, default=2); c.add_argument('--segments', type=int, default=3)
    c.add_argument('--zoom', type=float, default=2.6); c.add_argument('--guides', action='store_true')
    c.add_argument('--clefs', help='comma-separated per staff in a system, e.g. treble8,bass')
    A = ap.parse_args()
    if A.cmd == 'topdf':
        if len(A.files) < 2 or not A.files[-1].lower().endswith('.pdf'): sys.exit('usage: scan_tools.py topdf image1 [image2 ...] out.pdf')
        topdf(A.files[:-1], A.files[-1])
    elif A.cmd == 'extract': extract(A.pdf, A.outdir)
    elif A.cmd == 'staves': staves(A.page, A.out)
    elif A.cmd == 'crops': crops(A.page, A.staves, A.outdir, A.per_system, A.segments, A.zoom, A.guides, A.clefs.split(',') if A.clefs else None)
    else: ap.print_help()
