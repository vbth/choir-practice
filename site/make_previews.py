#!/usr/bin/env python3
"""Example previews of the website (fan of three score pages in the section "Beispiel-ZIP"): cover and both music pages of the score PDF, per language.

  python3 site/make_previews.py [--zip-dir DIR]

Takes the example packages of the current release (build_site.ZIPS, downloaded from build_site.REL unless --zip-dir holds them),
renders the score with the current templates and the layout stored in the package (pages, systems per page, date of the package),
and writes docs/img/example-cover-<lang>-<w>.png, example-page-1-<lang>-<w>.png and example-page-2-<lang>-<w>.png: greyscale PNG (A4), one file per width in WIDTHS.
Each width is rendered straight from the PDF (not shrunk from a big image), so the staff lines stay black and distinct; the page shows them at 160 or 240 CSS px
with srcset, i.e. 1x, 2x and 3x screens get a file with exactly one pixel per device pixel (retina optimised).
Run it after any change to the score templates (cover, header, footer), then site/build_site.py. Needs poppler (pdftoppm)."""
import glob, json, os, re, subprocess, sys, tempfile, urllib.request, zipfile
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from build_site import REL, ZIPS, OUT
from PIL import Image

WIDTHS = (160, 240, 320, 480, 720)   # 160 and 240 px displayed at 1x, 2x, 3x (see .fan in build_site.py)
RATIO = 1980 / 1400   # A4 as before
RENDER = os.path.join(HERE, '..', 'choir-practice', 'scripts', 'render_score.py')

# Renders the score PDF from the packed project data of one example ZIP and cuts out cover and music pages
def one(zip_path, work):
    d = os.path.join(work, os.path.splitext(os.path.basename(zip_path))[0]); zipfile.ZipFile(zip_path).extractall(d)
    spec_p = glob.glob(os.path.join(d, '4_*', '1_*', 'score.json'))[0]; lay = json.load(open(os.path.join(os.path.dirname(spec_p), 'layout.json'), encoding='utf-8'))
    xml = glob.glob(os.path.join(d, '1_*', '3_*.musicxml'))[0]; lang = json.load(open(spec_p, encoding='utf-8')).get('language', 'en')
    m = re.match(r'(\d{4}-\d{2}-\d{2})_', os.path.basename(zip_path))   # package names carry no date any more: use the date of the files in the ZIP
    date = m.group(1) if m else '%04d-%02d-%02d' % zipfile.ZipFile(zip_path).infolist()[0].date_time[:3]
    pdf = os.path.join(work, f'score_{lang}.pdf')
    subprocess.run([sys.executable, RENDER, xml, pdf, '--lang', lang, '--date', date, '--spec', spec_p,
                    '--force', f'pages={lay["pages"]},spp={lay["systems_per_page"]}'], check=True, capture_output=True)
    for w in WIDTHS:
        subprocess.run(['pdftoppm', '-png', '-scale-to-x', str(w), '-scale-to-y', str(round(w * RATIO)), '-f', '1', '-l', '3', pdf, os.path.join(work, f'p_{lang}_{w}')], check=True)
        for k, name in ((1, 'cover'), (2, 'page-1'), (3, 'page-2')):
            src = sorted(glob.glob(os.path.join(work, f'p_{lang}_{w}-*{k}.png')))[0]
            im = Image.open(src).convert('L'); assert im.size == (w, round(w * RATIO)), im.size
            out = os.path.join(OUT, 'img', f'example-{name}-{lang}-{w}.png'); im.save(out, optimize=True); print('written:', os.path.relpath(out, os.path.join(HERE, '..')))

def main():
    zip_dir = sys.argv[sys.argv.index('--zip-dir') + 1] if '--zip-dir' in sys.argv else None
    with tempfile.TemporaryDirectory() as work:
        for _, fn in ZIPS:
            z = os.path.join(zip_dir, fn) if zip_dir else os.path.join(work, fn)
            if not zip_dir: urllib.request.urlretrieve(REL + fn, z)
            one(z, work)

if __name__ == '__main__':
    main()
