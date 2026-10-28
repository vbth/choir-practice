#!/usr/bin/env python3
"""Preflight for a score page (scan or photo): staves, note heads, stem directions, pitches – measured.

  python3 preflight.py page.png --out DIR --clefs treble8,bass,treble8,bass,treble8,bass [--key -2] [--per-system 2] [--zoom 3]

Why: the global staff detector in scan_tools.py fails on tilted or curved photos and on pages with handwriting
(it can miss whole staves). This script fits the five staff lines LOCALLY (windows across the page, linear fit per
line), finds note heads (splitting chord blobs), measures each head's position against the local lines and
converts it to a pitch. It also reports stem directions: a staff with up- and down-stems has two voices.

Outputs in DIR:
  preflight.json            staves (line fits), heads (x, y, staff position, pitch, stems)
  preflight.txt             table of heads per staff, grouped by x (left to right), upper head first
  grid_sys<N>_seg<M>.png    crops with the fitted staff lines and a pitch label next to every head (look at them!)

--clefs   one clef per detected staff, top to bottom: treble, treble8 (tenor, sounds an octave lower), bass
--key     number of flats (negative) or sharps (positive) of the key signature, e.g. -2 for B flat major
Pitches are SOUNDING pitches. Accidentals printed in the music (sharps, flats, naturals before a note) are NOT
detected – look for them in the crops. Rhythm (flags, beams, dots, ties) is NOT measured: read it per voice.
"""
import os, sys, json, argparse
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi

LETTERS = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
FLAT_ORDER = ['B', 'E', 'A', 'D', 'G', 'C', 'F']
SHARP_ORDER = ['F', 'C', 'G', 'D', 'A', 'E', 'B']
# staff position 0 = bottom line; value = (letter index, octave) of the SOUNDING pitch on the bottom line
BOTTOM = {'treble': (2, 4), 'treble8': (2, 3), 'bass': (4, 2)}   # E4, E3, G2

def pitch_name(pos, clef, key):
    li, octv = BOTTOM[clef]
    n = li + pos
    letter = LETTERS[n % 7]; octave = octv + n // 7
    acc = ''
    if key < 0 and letter in FLAT_ORDER[:-key]: acc = 'b'
    if key > 0 and letter in SHARP_ORDER[:key]: acc = '#'
    return f'{letter}{acc}{octave}'

def groups(rows, gap=2):
    out, cur = [], []
    for r in rows:
        if cur and r - cur[-1] > gap: out.append(cur); cur = []
        cur.append(r)
    if cur: out.append(cur)
    return [sum(c) / len(c) for c in out]

def five_lines(centres, H):
    res, i = [], 0
    while i + 4 < len(centres):
        g = centres[i:i + 5]; d = np.diff(g)
        if d.max() - d.min() <= max(3, 0.25 * d.mean()) and 5 < d.mean() < H / 40:
            res.append(g); i += 5
        else: i += 1
    return res

def fit_staves(dark, W, H):
    win = max(60, int(W * 0.057)); step = max(30, win // 2)
    per_window = []
    for x0 in range(int(W * 0.15), W - win - int(W * 0.03), step):
        frac = dark[:, x0:x0 + win].mean(axis=1)
        centres = groups([i for i, v in enumerate(frac) if v > 0.45])
        per_window.append((x0 + win // 2, five_lines(centres, H)))
    counts = [len(s) for _, s in per_window]
    if not counts or max(counts) == 0: return [], counts
    mode = max(set(counts), key=counts.count)
    use = [(x, s) for x, s in per_window if len(s) == mode]
    staves = []
    for k in range(mode):
        fits = []
        for li in range(5):
            xs = [x for x, s in use]; ys = [s[k][li] for x, s in use]
            fits.append(np.polyfit(xs, ys, 1) if len(xs) >= 3 else np.array([0.0, float(np.mean(ys))]))
        staves.append(fits)
    return staves, counts

def line_y(fits, x): return [float(np.polyval(p, x)) for p in fits]

def local_lines(dark, fits, x):
    """Refine the five line positions at column x from the pixels around it (handles curved photos).
    Falls back to the global fit if any line cannot be found."""
    exp = line_y(fits, x); sp = (exp[4] - exp[0]) / 4
    half = int(3.5 * sp); x0, x1 = max(0, int(x - half)), min(dark.shape[1], int(x + half))
    ya = int(exp[0] - 0.8 * sp); yb = int(exp[4] + 0.8 * sp)
    reg = dark[ya:yb, x0:x1]
    keep = reg.mean(axis=0) < 0.55                      # drop columns that are stems or barlines
    if keep.sum() < 0.8 * sp * 2: return exp
    rows = reg[:, keep].mean(axis=1); found = []
    for e in exp:
        lo, hi = int(e - 0.45 * sp - ya), int(e + 0.45 * sp - ya)
        seg = rows[max(lo, 0):hi + 1]
        if len(seg) == 0 or seg.max() < 0.4: return exp
        w = np.clip(seg - 0.5 * seg.max(), 0, None); idx = np.arange(max(lo, 0), max(lo, 0) + len(seg))
        found.append(ya + float((idx * w).sum() / w.sum()))
    return found

def find_heads(dark, staves, clefs, key):
    out = []
    for si, fits in enumerate(staves):
        xm = dark.shape[1] // 2
        L = line_y(fits, xm); sp = (L[4] - L[0]) / 4
        y0 = int(max(0, L[0] - 4.5 * sp)); y1 = int(min(dark.shape[0], L[4] + 4.5 * sp))
        reg = dark[y0:y1, :]
        r = max(2, int(round(sp * 0.22)))
        yy, xx = np.ogrid[-r:r + 1, -r:r + 1]
        er = ndi.binary_erosion(reg, structure=(xx * xx + yy * yy) <= r * r)
        lab, n = ndi.label(er)
        for i in range(1, n + 1):
            ys, xs = np.where(lab == i)
            area = len(ys); w = xs.max() - xs.min() + 1; h = ys.max() - ys.min() + 1
            if area < 0.35 * sp * sp or w > 1.5 * sp or h < 0.6 * sp or h > 2.6 * sp: continue
            cx = xs.mean(); ymin, ymax = ys.min() + y0, ys.max() + y0
            cys = [ymin + 0.42 * sp, ymax - 0.42 * sp] if h >= 1.5 * sp else [ys.mean() + y0]
            for cy in cys:
                Lh = local_lines(dark, fits, cx); sph = (Lh[4] - Lh[0]) / 4
                pos = (Lh[4] - cy) / (sph / 2); p = int(round(pos))
                up = down = False
                for dx in range(int(0.3 * sph), int(0.85 * sph) + 1):
                    ya, yb = int(cy - 3 * sph - y0), int(cy - 0.7 * sph - y0)
                    if ya >= 0 and reg[ya:yb, int(cx + dx)].mean() > 0.85: up = True
                    ya, yb = int(cy + 0.7 * sph - y0), int(cy + 3 * sph - y0)
                    if yb < reg.shape[0] and reg[ya:yb, int(cx - dx)].mean() > 0.85: down = True
                out.append({'staff': si, 'x': round(float(cx), 1), 'y': round(float(cy), 1), 'pos': round(float(pos), 2),
                            'off': round(abs(pos - p), 2), 'pitch': pitch_name(p, clefs[si], key),
                            'stem_up': up, 'stem_down': down})
    return sorted(out, key=lambda h: (h['staff'], h['x']))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('page'); ap.add_argument('--out', required=True)
    ap.add_argument('--clefs', default=''); ap.add_argument('--key', type=int, default=0)
    ap.add_argument('--per-system', type=int, default=2); ap.add_argument('--zoom', type=float, default=3.0)
    A = ap.parse_args(); os.makedirs(A.out, exist_ok=True)
    im = Image.open(A.page).convert('L'); g = np.array(im).astype(float); H, W = g.shape
    dark = g < (np.percentile(g, 60) - 60)
    staves, counts = fit_staves(dark, W, H)
    print(f'staves found by local line fit: {len(staves)} (windows with N staves: '
          + ', '.join(f'{n}x{counts.count(n)}' for n in sorted(set(counts))) + ')')
    print('CHECK: count the staves on the page image yourself. A different number means the fit is unreliable.')
    clefs = [c.strip() for c in A.clefs.split(',') if c.strip()] or ['treble'] * len(staves)
    if len(clefs) != len(staves):
        sys.exit(f'--clefs has {len(clefs)} entries but {len(staves)} staves were found')
    heads = find_heads(dark, staves, clefs, A.key)
    # scan quality gate: clear criteria, ABORT = ask the user for a better scan (exit code 3)
    sp_px = float(np.median([(line_y(f, W / 2)[4] - line_y(f, W / 2)[0]) / 4 for f in staves])) if staves else 0.0
    contrast = float(np.percentile(g, 60) - np.percentile(g, 2))
    mode_share = (max(counts.count(n) for n in set(counts)) / len(counts)) if counts else 0.0
    off_share = (sum(h['off'] > 0.3 for h in heads) / len(heads)) if heads else 1.0
    abort, warn = [], []
    if not staves: abort.append('no staves found')
    if sp_px < 8: abort.append(f'staff space {sp_px:.1f} px < 8 px (resolution too low)')
    elif sp_px < 12: warn.append(f'staff space {sp_px:.1f} px < 12 px (small, expect more uncertain spots)')
    if contrast < 40: abort.append(f'contrast {contrast:.0f} < 40 (too faint or too dark)')
    if mode_share < 0.6: abort.append(f'staff count differs between windows (share of the usual count {mode_share:.0%} < 60 %)')
    if off_share > 0.5: abort.append(f'{off_share:.0%} of the heads are not centred on lines or spaces (blur or distortion)')
    elif off_share > 0.25: warn.append(f'{off_share:.0%} of the heads are off-centre')
    print(f'SCAN QUALITY: staff space {sp_px:.1f} px, contrast {contrast:.0f}, window agreement {mode_share:.0%}, off-centre heads {off_share:.0%}')
    for w in warn: print('  WARN:', w)
    for a in abort: print('  ABORT:', a)
    if abort:
        print('VERDICT: ABORT. Stop and ask the user for a better scan or photo (flat, sharp, even light, at least 150 dpi); do not transcribe from this page.')
        if not staves: sys.exit(3)
    # report
    lines = []
    for si in range(len(staves)):
        hs = [h for h in heads if h['staff'] == si]
        lines.append(f'staff {si} ({clefs[si]}): {len(hs)} heads; stems up {sum(h["stem_up"] for h in hs)}, '
                     f'down {sum(h["stem_down"] for h in hs)}'
                     + ('  -> up AND down stems: two voices on this staff' if any(h['stem_up'] for h in hs) and any(h['stem_down'] for h in hs) else ''))
        cur = []
        for h in hs:
            if cur and h['x'] - cur[-1]['x'] > 0.9 * 13: lines.append('   x=%d: ' % cur[0]['x'] + '  '.join(f"{c['pitch']}{'^' if c['stem_up'] else ''}{'v' if c['stem_down'] else ''}" + ('?' if c['off'] > 0.3 else '') for c in sorted(cur, key=lambda c: -c['pos']))); cur = []
            cur.append(h)
        if cur: lines.append('   x=%d: ' % cur[0]['x'] + '  '.join(f"{c['pitch']}{'^' if c['stem_up'] else ''}{'v' if c['stem_down'] else ''}" + ('?' if c['off'] > 0.3 else '') for c in sorted(cur, key=lambda c: -c['pos'])))
    lines.append('legend: ^ stem up, v stem down, ? head is not centred on a line/space (check the crop). Accidentals and rhythm are not measured.')
    txt = '\n'.join(lines); print(txt)
    open(os.path.join(A.out, 'preflight.txt'), 'w').write(txt)
    json.dump({'page': A.page, 'clefs': clefs, 'key': A.key, 'window_counts': counts,
               'staves': [[list(map(float, p)) for p in f] for f in staves], 'heads': heads},
              open(os.path.join(A.out, 'preflight.json'), 'w'), indent=1)
    # crops with grid and labels
    rgb = Image.open(A.page).convert('RGB'); S = A.zoom
    try: font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 13)
    except Exception: font = ImageFont.load_default()
    systems = [list(range(i, min(i + A.per_system, len(staves)))) for i in range(0, len(staves), A.per_system)]
    for sn, sysst in enumerate(systems, 1):
        for seg, (xa, xb) in enumerate([(0.10, 0.58), (0.52, 1.0)], 1):
            x0, x1 = int(W * xa), int(W * xb); parts = []
            for si in sysst:
                f = staves[si]; xm = (x0 + x1) / 2; L = line_y(f, xm); sp = (L[4] - L[0]) / 4
                ya, yb = int(max(0, L[0] - 6 * sp)), int(min(H, L[4] + 6 * sp))
                c = rgb.crop((x0, ya, x1, yb)).resize((int((x1 - x0) * S), int((yb - ya) * S)), Image.LANCZOS)
                d = ImageDraw.Draw(c)
                for p in f: d.line([(0, (np.polyval(p, x0) - ya) * S), (c.width, (np.polyval(p, x1) - ya) * S)], fill=(255, 0, 0), width=1)
                for h in heads:
                    if h['staff'] == si and x0 <= h['x'] <= x1:
                        d.text(((h['x'] - x0) * S + 9 * S / 2, (h['y'] - ya) * S - 8), h['pitch'], fill=(0, 120, 0), font=font)
                parts.append(c)
            hh = sum(c.height for c in parts) + 10 * (len(parts) - 1)
            o = Image.new('RGB', (parts[0].width, hh), 'white'); y = 0
            for c in parts: o.paste(c, (0, y)); y += c.height + 10
            o.save(os.path.join(A.out, f'grid_sys{sn}_seg{seg}.png'))
    print('crops:', ', '.join(sorted(f for f in os.listdir(A.out) if f.startswith('grid_'))))
    if abort: sys.exit(3)

if __name__ == '__main__':
    main()
