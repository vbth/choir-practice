"""Turn stroked SVG elements (class k / n) into filled brush strokes of varying width."""
import math, random, re, sys
from svgpathtools import parse_path

src, dst = sys.argv[1], sys.argv[2]
scale_var = float(sys.argv[3]) if len(sys.argv) > 3 else 0.9
rnd = random.Random(11)


def attrs(tag):
    return dict(re.findall(r'(\w[\w-]*)="([^"]*)"', tag))


def circle_d(a):
    cx, cy, r = float(a['cx']), float(a['cy']), float(a['r'])
    return f'M{cx-r} {cy}A{r} {r} 0 1 0 {cx+r} {cy}A{r} {r} 0 1 0 {cx-r} {cy}Z'


def rect_d(a):
    x, y, w, h = (float(a[k]) for k in ('x', 'y', 'width', 'height'))
    r = float(a.get('rx', 0))
    if not r:
        return f'M{x} {y}H{x+w}V{y+h}H{x}Z'
    return (f'M{x+r} {y}H{x+w-r}A{r} {r} 0 0 1 {x+w} {y+r}V{y+h-r}A{r} {r} 0 0 1 {x+w-r} {y+h}'
            f'H{x+r}A{r} {r} 0 0 1 {x} {y+h-r}V{y+r}A{r} {r} 0 0 1 {x+r} {y}Z')


def brush(d, base):
    out = []
    path = parse_path(d)
    for sub in path.continuous_subpaths():
        L = sub.length()
        if L < 0.5:
            continue
        closed = sub.isclosed()
        n = max(8, int(L / 1.5))
        ph = [rnd.uniform(0, 6.3) for _ in range(3)]
        fr = [rnd.uniform(0.02, 0.05), rnd.uniform(0.06, 0.11), rnd.uniform(0.15, 0.25)]
        left, right = [], []
        for i in range(n + 1):
            s = L * i / n
            try:
                t = sub.ilength(min(s, L * (1 - 1e-6)), s_tol=1e-3) if 0 < s < L else (0 if s == 0 else 1)
            except ValueError:
                t = s / L
            seg_i, seg_t = sub.T2t(t) if hasattr(sub, 'T2t') else (None, None)
            p = sub.point(t)
            try:
                tan = sub.unit_tangent(t)
            except Exception:
                tan = 1
            nx, ny = -tan.imag, tan.real
            v = (0.55 * math.sin(fr[0] * s + ph[0]) + 0.3 * math.sin(fr[1] * s + ph[1])
                 + 0.15 * math.sin(fr[2] * s + ph[2]))
            w = base * (1 + scale_var * 0.5 * v)
            if not closed:
                e = min(s, L - s)
                w *= 0.45 + 0.55 * min(1, e / 10)
            w = max(w, base * 0.3)
            left.append((p.real + nx * w / 2, p.imag + ny * w / 2))
            right.append((p.real - nx * w / 2, p.imag - ny * w / 2))
        fmt = lambda pts: 'L'.join(f'{x:.1f} {y:.1f}' for x, y in pts)
        if closed:
            out.append(f'M{fmt(left)}Z M{fmt(right[::-1])}Z')
        else:
            out.append(f'M{fmt(left + right[::-1])}Z')
        # round joins at the corners between segments
        for seg in sub[1:]:
            a = seg.start
            out.append(f'M{a.real - base*0.45:.1f} {a.imag:.1f}a{base*0.45:.2f} {base*0.45:.2f} 0 1 0 {base*0.9:.2f} 0a{base*0.45:.2f} {base*0.45:.2f} 0 1 0 {-base*0.9:.2f} 0Z')
    return ' '.join(out)


def repl(m):
    tag = m.group(0)
    a = attrs(tag)
    cls = a.get('class', '').split()
    if not ({'k', 'n'} & set(cls)):
        return tag
    name = m.group(1)
    d = a.get('d') if name == 'path' else circle_d(a) if name == 'circle' else rect_d(a)
    sw = 4.5
    style = a.get('style', '')
    mw = re.search(r'stroke-width:([\d.]+)', style)
    if mw:
        sw = float(mw.group(1))
    keep = ''
    fill_cls = [c for c in cls if c not in ('k', 'n')]
    if fill_cls or 'fill:' in style:
        fstyle = re.sub(r'stroke-width:[\d.]+;?', '', style)
        extra = f' style="{fstyle}"' if fstyle else ''
        keep = f'<path class="{" ".join(fill_cls)}" d="{d}"{extra}/>'
    ink_cls = 'nf' if 'n' in cls else 'd'
    return keep + f'<path class="{ink_cls}" fill-rule="nonzero" d="{brush(d, sw * 1.05)}"/>'


s = open(src).read()
body_start = s.index('</style>')
head, body = s[:body_start], s[body_start:]
body = re.sub(r'<(path|circle|rect)\b[^>]*/>', repl, body)
open(dst, 'w').write(head + body)
