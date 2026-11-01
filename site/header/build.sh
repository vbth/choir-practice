#!/bin/sh
# Rebuilds all header images from header-src.svg into docs/img/. Needs: python3 + svgpathtools, node + playwright.
set -e
HERE=$(cd "$(dirname "$0")" && pwd); ROOT=$(dirname "$(dirname "$HERE")"); T=$(mktemp -d)
python3 "$HERE/ink.py" "$HERE/header-src.svg" "$T/ink.svg" 0.9
sed -i 's|scale="3.5"|scale="2.5"|' "$T/ink.svg"
python3 - "$T" <<'PY'
import sys
t = sys.argv[1]; s = open(t + '/ink.svg').read()
s = s.replace('viewBox="0 0 1280 640"', 'viewBox="30.5 0 1219 640"', 1)
i = s.rfind('</svg>')
open(t + '/og.svg', 'w').write(s[:i] + '<rect class="fr" x="35.5" y="5" width="1209" height="630" style="stroke-width:10"/>\n' + s[i:])
PY
node "$HERE/render.js" "$T"
# link preview: white margin around the drawing, so messengers that round the corners (iMessage and others) do not cut off the black frame
python3 - "$T/og-raw.png" "$ROOT/docs/img/og.png" <<'PY'
import sys
from PIL import Image
src, dst = sys.argv[1:3]; im = Image.open(src).convert('RGB'); W, H = im.size; k = 0.84
small = im.resize((round(W * k), round(H * k)), Image.Resampling.LANCZOS)
canvas = Image.new('RGB', (W, H), 'white'); canvas.paste(small, ((W - small.width) // 2, (H - small.height) // 2)); canvas.save(dst, optimize=True)
PY
# header PNGs (website and README): 3x, small palette (the drawing has black, white, red and their anti-aliasing)
python3 - "$T" "$ROOT/docs/img" <<'PY'
import sys
from PIL import Image
t, out = sys.argv[1:3]
for src, dst in (('out-light.png', 'header.png'), ('out-dark.png', 'header-dark.png')):
    Image.open(f'{t}/{src}').convert('RGB').quantize(colors=48, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).save(f'{out}/{dst}', optimize=True)
PY
echo "done: docs/img/header.png, header-dark.png, og.png"
