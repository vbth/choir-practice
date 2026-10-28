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
cp "$T/og-raw.png" "$ROOT/docs/img/og.png"
# header PNGs (website and README): 3x, small palette (the drawing has black, white, red and their anti-aliasing)
python3 - "$T" "$ROOT/docs/img" <<'PY'
import sys
from PIL import Image
t, out = sys.argv[1:3]
for src, dst in (('out-light.png', 'header.png'), ('out-dark.png', 'header-dark.png')):
    Image.open(f'{t}/{src}').convert('RGB').quantize(colors=48, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).save(f'{out}/{dst}', optimize=True)
PY
echo "done: docs/img/header.png, header-dark.png, og.png"
