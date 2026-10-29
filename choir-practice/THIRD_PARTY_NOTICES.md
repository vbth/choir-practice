# Third-party notices

Checked on 2026-10-26 against the sources named below (summaries, not legal advice). Entries marked **confirmed** were read in the licence text or the official page; **to check** means not verified.

## Bundled in this skill

| Component | Where | Licence | Status |
|---|---|---|---|
| IBM Plex Sans, Plex Sans Condensed (fonts) | `assets/fonts/` | SIL Open Font License 1.1, Copyright © 2017 IBM Corp., Reserved Font Name "Plex". Use, embedding in PDFs and redistribution are allowed; do not sell the fonts alone, keep the notice, do not use the name "Plex" for modified fonts. | **confirmed** (`assets/fonts/OFL-IBMPlexSans.txt`) |
| EU label "AI" (basic icon, round, SVG, black): file `LABEL_AI_black.svg` of the EU icon set, supplied by the owner on 2026-10-29. viewBox cropped to the circle and styles inlined, shape unchanged. Used in every PDF and Markdown footer | `assets/eu-ai-basic.svg` | as the next row: free use without attribution | **confirmed** for the file (owner); the EU page itself could not be fetched here |
| EU label "AI GENERATED" / "AI MODIFIED" (SVG, black, cropped, styles inlined). "AI GENERATED" is used in the album art, the header image and the website footer | `assets/eu-ai-generated.svg`, `assets/eu-ai-modified.svg` | European Commission, [EU icons for labelling AI-generated content](https://digital-strategy.ec.europa.eu/en/policies/eu-icons-labelling-ai-generated-content) (page of 2026-09-24): "made publicly available for everyone to use freely", "without the need for attribution". Use is optional and does not by itself establish compliance with Article 50 AI Act. Non-signatories of the Code of Practice must not imply adherence to it. The page does not say anything about recolouring, cropping or commercial use; the skill uses the black variant, cropped to the label, unchanged in shape. | **confirmed** for free use without attribution; recolouring and cropping not addressed (low risk, ask the AI Act Service Desk if it matters) |

## Repository only (website and README images, not part of the `.skill`)

| Component | Where | Licence | Status |
|---|---|---|---|
| IBM Plex Sans, Sans Condensed (website fonts, WOFF2, self-hosted, no Google request) | `docs/fonts/` | SIL Open Font License 1.1, Copyright © 2017 IBM Corp., Reserved Font Name "Plex"; licence text in `docs/fonts/OFL-IBMPlexSans.txt`; WOFF2 files from the npm package `@fontsource/ibm-plex-sans` | **confirmed** (`docs/fonts/OFL-IBMPlexSans.txt`) |
| EU label copies for the website and the README footers: `ai-generated.svg`, `ai-basic.svg` (black) and `ai-generated-dark.svg`, `ai-basic-dark.svg` (white, made from the black ones by a script) | `docs/img/` | as the EU label above; the white variant is a recolouring, which the EU page does not address as far as read | **to check** (recolouring) |

Open question (2026-10-29): secondary sources (not the official page, which could not be fetched) describe the EU set as three icons (basic "AI", fully AI-generated, partially AI-modified), each in black, white and two 50 %-transparent versions, as SVG and PNG. The skill bundles the round "AI" icon (black) and the two long labels (black); the white and transparent versions are not bundled (the white copies for dark mode are made by a script, a recolouring the EU page does not address as far as read).

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
