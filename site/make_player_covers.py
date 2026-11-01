#!/usr/bin/env python3
"""Album covers of the website player (docs/img/cover-de.jpg, cover-en.jpg).

  python3 site/make_player_covers.py

Builds the cover of the example pack exactly as the skill does (build_score.py, make_cover.py from site/example/score.<lang>.json), then recolours it
from green to red to match the site: hue shift -100 degrees, saturation x1.3. The label "AI" stays black and white. The cover inside the example package stays green.
Run it after any change to make_cover.py, then site/build_site.py."""
import os, subprocess, sys, tempfile
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); SK = os.path.join(HERE, '..', 'choir-practice', 'scripts')
HUE_SHIFT, SAT = -100, 1.3

def recolour(src, dst):
    hsv = np.array(Image.open(src).convert('RGB').convert('HSV')).astype(float)
    hsv[..., 0] = (hsv[..., 0] + HUE_SHIFT / 360 * 256) % 256
    hsv[..., 1] = np.clip(hsv[..., 1] * SAT, 0, 255)
    Image.fromarray(hsv.round().astype(np.uint8), 'HSV').convert('RGB').save(dst, 'JPEG', quality=90, subsampling=0, optimize=True)

# Reuses the skill's album-art generator and recolours it to the site palette
def main():
    with tempfile.TemporaryDirectory() as w:
        for lang in ('de', 'en'):
            spec = os.path.join(HERE, 'example', f'score.{lang}.json'); xml = os.path.join(w, f'{lang}.musicxml'); green = os.path.join(w, f'{lang}.jpg')
            subprocess.run([sys.executable, os.path.join(SK, 'build_score.py'), spec, xml], check=True, capture_output=True)
            subprocess.run([sys.executable, os.path.join(SK, 'make_cover.py'), spec, xml, green], check=True)
            out = os.path.join(HERE, '..', 'docs', 'img', f'cover-{lang}.jpg'); recolour(green, out); print('written:', os.path.relpath(out, os.path.join(HERE, '..')))

if __name__ == '__main__':
    main()
