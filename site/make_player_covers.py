#!/usr/bin/env python3
"""Album covers of the website player (docs/img/cover-de.jpg, cover-en.jpg).

  python3 site/make_player_covers.py

Builds the cover of the example pack exactly as the skill does (build_score.py, make_cover.py from site/example/score.<lang>.json). The example scores carry
"cover": {"color": "#d9251d"} (the red of the website), so the hue comes from that colour and the cover inside the example package is the same red one.
Run it after any change to make_cover.py, then site/make_web_audio.py --cover-only and site/build_site.py."""
import os, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); SK = os.path.join(HERE, '..', 'choir-practice', 'scripts')

# Reuses the skill's album-art generator; the colour comes from the example score
def main():
    with tempfile.TemporaryDirectory() as w:
        for lang in ('de', 'en'):
            spec = os.path.join(HERE, 'example', f'score.{lang}.json'); xml = os.path.join(w, f'{lang}.musicxml')
            subprocess.run([sys.executable, os.path.join(SK, 'build_score.py'), spec, xml], check=True, capture_output=True)
            out = os.path.join(HERE, '..', 'docs', 'img', f'cover-{lang}.jpg')
            subprocess.run([sys.executable, os.path.join(SK, 'make_cover.py'), spec, xml, out], check=True); print('written:', os.path.relpath(out, os.path.join(HERE, '..')))

if __name__ == '__main__':
    main()
