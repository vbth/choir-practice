#!/usr/bin/env python3
"""Visual regression test for the engraved score pages (Verovio -> PDF).

  python3 tests/visual/visual_diff.py compare REF_DIR [--out DIFF_DIR]   render the example score, compare every page with REF_DIR
  python3 tests/visual/visual_diff.py update  REF_DIR                    render and write the page PNGs as the new references
  python3 tests/visual/visual_diff.py selftest                           the comparison itself: identical passes, a shifted page fails

The example is site/example/score.en.json through build_score.py and render_score.py with a fixed date; the PDF pages become greyscale
PNGs (pdftoppm, DPI). A page fails when more than TOL of its pixels differ by more than LEVEL grey levels, or when its size or the page count
differs. The references are not in git: they are the release asset visual-refs.zip (see .github/workflows/visual-refs.yml).
Needs the packages of scripts/requirements-stable.txt and poppler (pdftoppm)."""
import argparse, glob, os, shutil, subprocess, sys, tempfile
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
SCRIPTS = os.path.join(REPO, 'choir-practice', 'scripts'); SPEC = os.path.join(REPO, 'site', 'example', 'score.en.json')
DPI = 70; LEVEL = 64; TOL = 0.001; DATE = '2026-01-31'

def render(work):
    """Example score -> page PNGs `p1.png`, `p2.png`, ... in `work`; returns the sorted list of paths."""
    xml, pdf = os.path.join(work, 's.musicxml'), os.path.join(work, 's.pdf')
    subprocess.run([sys.executable, os.path.join(SCRIPTS, 'build_score.py'), SPEC, xml], check=True, capture_output=True)
    subprocess.run([sys.executable, os.path.join(SCRIPTS, 'render_score.py'), xml, pdf, '--lang', 'en', '--date', DATE, '--spec', SPEC], check=True, capture_output=True)
    subprocess.run(['pdftoppm', '-r', str(DPI), '-gray', '-png', pdf, os.path.join(work, 'p')], check=True)
    out = []
    for f in sorted(glob.glob(os.path.join(work, 'p-*.png'))):
        n = int(os.path.basename(f)[2:-4]); dst = os.path.join(work, f'p{n}.png'); os.replace(f, dst); out.append(dst)
    return sorted(out, key=lambda f: int(os.path.basename(f)[1:-4]))

def diff_pages(ref, new):
    """(share of differing pixels, diff image or None when the sizes differ)."""
    a, b = Image.open(ref).convert('L'), Image.open(new).convert('L')
    if a.size != b.size: return 1.0, None
    x, y = np.asarray(a, dtype=np.int16), np.asarray(b, dtype=np.int16)
    bad = np.abs(x - y) > LEVEL
    img = np.stack([np.where(bad, 255, y), np.where(bad, 0, y), np.where(bad, 0, y)], axis=-1).astype(np.uint8)   # new page, differences in red
    return float(bad.mean()), Image.fromarray(img)

def compare(ref_dir, new_files, out_dir=None):
    ref = sorted(glob.glob(os.path.join(ref_dir, 'p*.png')), key=lambda f: int(os.path.basename(f)[1:-4]))
    problems = []
    if len(ref) != len(new_files): problems.append(f'page count: reference {len(ref)}, now {len(new_files)}')
    for r, n in zip(ref, new_files):
        share, img = diff_pages(r, n); name = os.path.basename(r)
        print(f'{name}: {share * 100:.3f} % of the pixels differ (limit {TOL * 100:.3f} %)')
        if share > TOL:
            problems.append(f'{name}: {share * 100:.3f} % differ' + ('' if img else ' (page size changed)'))
            if out_dir and img:
                os.makedirs(out_dir, exist_ok=True); img.save(os.path.join(out_dir, 'diff-' + name))
    return problems

def selftest():
    with tempfile.TemporaryDirectory() as w:
        page = np.full((818, 578), 255, dtype=np.uint8); page[100:700:12, 60:520] = 0   # staff-line-like page
        Image.fromarray(page).save(os.path.join(w, 'a.png')); Image.fromarray(page).save(os.path.join(w, 'same.png'))
        Image.fromarray(np.roll(page, 4, axis=0)).save(os.path.join(w, 'shifted.png'))
        same, _ = diff_pages(os.path.join(w, 'a.png'), os.path.join(w, 'same.png')); moved, _ = diff_pages(os.path.join(w, 'a.png'), os.path.join(w, 'shifted.png'))
    assert same == 0 and moved > TOL, (same, moved)
    print(f'selftest ok: identical {same * 100:.3f} %, shifted by 4 px {moved * 100:.3f} % (limit {TOL * 100:.3f} %)')

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('cmd', choices=['compare', 'update', 'selftest']); ap.add_argument('ref', nargs='?'); ap.add_argument('--out')
    A = ap.parse_args()
    if A.cmd == 'selftest': return selftest()
    if not A.ref: sys.exit('REF_DIR missing')
    with tempfile.TemporaryDirectory() as w:
        pages = render(w)
        if A.cmd == 'update':
            shutil.rmtree(A.ref, ignore_errors=True); os.makedirs(A.ref)
            for p in pages: shutil.copy(p, A.ref)
            print(f'{len(pages)} reference pages written to {A.ref}'); return
        problems = compare(A.ref, pages, A.out)
    if problems:
        print('VISUAL DIFF FAILED:'); [print('  ' + p) for p in problems]
        print('Intended change? Run the workflow "Visual references" on this branch and check the diff images in the job artifacts first.')
        sys.exit(1)
    print(f'visual diff ok: {len(pages)} pages')

if __name__ == '__main__':
    main()
