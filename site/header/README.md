# Header image: source and files

[`header-src.svg`](header-src.svg) is the editable source (clean strokes). The images in `docs/img/` are generated, with brush-stroke outlines; never edit them by hand. There is no SVG on the page on purpose: browsers compute the "rough" filter as a bitmap, so an SVG turns blurry on phones and when zooming. The PNGs are rendered at 3x and shown at half size or less.

## Changing the image
1. Edit [`site/header/header-src.svg`](header-src.svg).
2. Run [`site/header/build.sh`](build.sh) (needs `pip install svgpathtools`, node with playwright). It writes the three image files below.
3. Look at [`docs/img/header.png`](../../docs/img/header.png) and `header-dark.png`.
4. Run `python site/build_site.py` if text, alt or image sizes changed (CI fails if `docs/` is not up to date).
5. Commit everything in the list and push.

## Files that change with every image change
| File | Used for | Size |
|---|---|---|
| [`docs/img/header.png`](../../docs/img/header.png) | website banner and README, light (`<picture>`, shown at 1280 x 640; small palette) | 3840 x 1920 |
| [`docs/img/header-dark.png`](../../docs/img/header-dark.png) | the same, dark | 3840 x 1920 |
| [`docs/img/og.png`](../../docs/img/og.png) | link preview (Open Graph, light) | 2400 x 1260 |

Only if something else changes: [`site/build_site.py`](../../site/build_site.py) (alt text `og_alt`, og image size), [`docs/index.html`](../../docs/index.html) and [`docs/en/index.html`](../../docs/en/index.html) (generated), [`CHANGELOG.md`](../../CHANGELOG.md) and [`choir-practice/CHANGELOG.md`](../../choir-practice/CHANGELOG.md) (identical copies).

Notes: the sheet of music has a footer with the EU label ([`choir-practice/assets/eu-ai-generated.svg`](../../choir-practice/assets/eu-ai-generated.svg), pasted as a nested `<svg>` with classes `d` and `w` so it follows dark mode); no grey tones; [`ink.py`](ink.py) drops transform attributes on stroked elements, so put transforms on a wrapping `<g>`. Link previews on social networks update late (cache).
