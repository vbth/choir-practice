# Third-party notices

Checked on 2026-10-26 against the sources named below (summaries, not legal advice). Entries marked **confirmed** were read in the licence text or the official page; **to check** means not verified.

## Bundled in this skill

| Component | Where | Licence | Status |
|---|---|---|---|
| IBM Plex Sans, Plex Sans Condensed (fonts) | `assets/fonts/` | SIL Open Font License 1.1, Copyright © 2017 IBM Corp., Reserved Font Name "Plex". Use, embedding in PDFs and redistribution are allowed; do not sell the fonts alone, keep the notice, do not use the name "Plex" for modified fonts. | **confirmed** (`assets/fonts/OFL-IBMPlexSans.txt`) |
| EU labels, complete official set (12 SVG: "AI", "AI GENERATED", "AI MODIFIED", each black and white, each also 50 % transparent): files supplied by the owner on 2026-10-29, content unchanged, spaces in the file names replaced by underscores | `assets/eu-labels/` | European Commission, [EU icons for labelling AI-generated content](https://digital-strategy.ec.europa.eu/en/policies/eu-icons-labelling-ai-generated-content) (page of 2026-09-24): "made publicly available for everyone to use freely", "without the need for attribution". Use is optional and does not by itself establish compliance with Article 50 AI Act. Non-signatories of the Code of Practice must not imply adherence to it. | **confirmed** for free use without attribution (the page text as recorded on 2026-10-26; the page could not be fetched again on 2026-10-29) |
| Working copies of the black labels: viewBox cropped to the label, styles inlined, shapes unchanged (paths identical to the official files, checked). "AI" is the one label used everywhere: every PDF and Markdown footer, the album art and the website footer; "AI GENERATED" only in the header image of the website | `assets/eu-ai-basic.svg`, `assets/eu-ai-generated.svg`, `assets/eu-ai-modified.svg` (not used, kept for another policy) | as above; cropping and inlining only | **confirmed** |

## Repository only (website and README images, not part of the `.skill`)

| Component | Where | Licence | Status |
|---|---|---|---|
| IBM Plex Sans, Sans Condensed (website fonts, WOFF2, self-hosted, no Google request) | `docs/fonts/` | SIL Open Font License 1.1, Copyright © 2017 IBM Corp., Reserved Font Name "Plex"; licence text in `docs/fonts/OFL-IBMPlexSans.txt`; WOFF2 files from the npm package `@fontsource/ibm-plex-sans` | **confirmed** (`docs/fonts/OFL-IBMPlexSans.txt`) |
| EU label copies for the website footer and the README footers: `ai-basic.svg` (black, from the working copy above) and `ai-basic-dark.svg` (white, built from the official white file of `assets/eu-labels/`, same crop, styles inlined) | `docs/img/` | as above | **confirmed** |


## Used at run time (installed by `scripts/setup.sh`, not bundled)

| Component | Use | Licence | Status |
|---|---|---|---|
| Verovio 6.3 | score engraving | LGPL-3.0 ([licensing page](https://book.verovio.org/introduction/licensing.html)). **Condition: visible credit to Verovio** – the README of every package says "engraved with Verovio (verovio.org)". Changes to Verovio itself would have to be published under LGPL-3.0; the skill does not modify it. | **confirmed** |
| Leland (music font inside Verovio) | notation glyphs in the score PDFs | SIL Open Font License 1.1 ([upstream](https://github.com/gameleaf/Leland)); embedding in PDFs is allowed | **confirmed** (upstream page); copyright holder not named there |
| MuseScore General (soundfont) | sound of the practice audio | MIT, parts public domain or CC0 (Debian copyright file of the package `musescore-general-soundfont`); the soundfont is a sample bank, the MuseScore program is not used | **confirmed** (package copyright file); the audio rendered with it is not a copy of the soundfont |
| FluidR3_GM (fallback soundfont) | same | MIT, Copyright © 2000-2002, 2008 Frank Wen (Debian copyright file of `fluid-soundfont-gm`) | **confirmed** |
| CairoSVG | SVG to PDF | LGPL-3.0-or-later | **confirmed** (package metadata) |
| lxml, pypdf | XML, PDF | BSD-3-Clause | **confirmed** (package metadata) |
| mido | MIDI | MIT | **confirmed** (package metadata) |
| ReportLab | PDF documents | BSD | **confirmed** (package metadata) |
| Pillow | images | MIT-CMU | **confirmed** (package metadata) |
| NumPy | audio analysis | BSD-3-Clause and others (0BSD, MIT, Zlib, CC0) | **confirmed** (package metadata) |
| SciPy | signal processing | BSD-style | **confirmed** (package metadata, licence text not read) |
| poppler-utils (`pdftoppm`) | PDF pages to images | GPL-2.0-or-later (Debian package; recalled, not read) | **to check** |
| fonts-dejavu-core (DejaVu Sans) | only for the debug images of `preflight.py`; not in any package | free Bitstream Vera / DejaVu licence (recalled, not read) | **to check** |
| FluidSynth 2.3 | MIDI to audio | LGPL-2.1 | **to check** (not read) |
| FFmpeg (with LAME) | audio mixing, MP3 encoding | the build used here is GPL-enabled (`--enable-gpl`, libmp3lame); applies to the programs, not to files made with them | **confirmed** for the build flags, **to check** for conditions of your own distribution |

None of the run-time components is shipped in the skill or in a package, so their licences create no duties for users of the skill beyond the Verovio credit; they matter only if someone redistributes these programs.

## Output of the skill

Packages contain the engraved score, audio and documents derived from the user's source. The rights to the music, text and source stay with the rights holders. The skill grants no rights and gives no legal advice (see the "Rights" section of each package's README).

## Licence of the skill itself

PolyForm Noncommercial License 1.0.0 (SPDX `PolyForm-Noncommercial-1.0.0`, see `LICENSE`, unmodified official text): free for any noncommercial purpose (personal use, hobby, charitable, educational, public bodies); commercial use needs a separate licence from the author. No author name is given on purpose, so there is no `Required Notice` line. The licences of the bundled assets above stay as stated and are not changed by this licence.
