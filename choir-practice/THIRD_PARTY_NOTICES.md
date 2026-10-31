# Third-party notices

Checked on 2026-10-26 and 2026-10-29 against the sources named below (summaries, not legal advice). Entries marked **confirmed** were read in the licence text, the package copyright file or the official page; **to check** would mean not verified (no entry is marked so at present).

## Bundled in this skill

| Component | Where | Licence | Status |
|---|---|---|---|
| IBM Plex Sans, Plex Sans Condensed (fonts) | `assets/fonts/` | SIL Open Font License 1.1, Copyright © 2017 IBM Corp., Reserved Font Name "Plex". Use, embedding in PDFs and redistribution are allowed; do not sell the fonts alone, keep the notice, do not use the name "Plex" for modified fonts. | **confirmed** (`assets/fonts/OFL-IBMPlexSans.txt`) |
| EU labels, complete official set (12 SVG: "AI", "AI GENERATED", "AI MODIFIED", each black and white, each also 50 % transparent): files supplied by the owner on 2026-10-29, content unchanged, spaces in the file names replaced by underscores | `assets/eu-labels/` | European Commission, [EU icons for labelling AI-generated content](https://digital-strategy.ec.europa.eu/en/policies/eu-icons-labelling-ai-generated-content) (page of 2026-09-24): "made publicly available for everyone to use freely", "without the need for attribution". Use is optional and does not by itself establish compliance with Article 50 AI Act. Non-signatories of the Code of Practice must not imply adherence to it. | **confirmed** for free use without attribution (the page text as recorded on 2026-10-26; the page could not be fetched again on 2026-10-29) |
| Working copies of the black labels: viewBox cropped to the label, styles inlined, shapes unchanged (paths identical to the official files, checked). "AI" is the one label used everywhere: every PDF and Markdown footer, the album art and the website footer; "AI GENERATED" only in the header image of the website | `assets/eu-ai-basic.svg`, `assets/eu-ai-generated.svg`, `assets/eu-ai-modified.svg` (not used, kept for another policy) | as above; cropping and inlining only | **confirmed** |
| GitHub mark (project line in every PDF and Markdown footer, linked to the repository): path data of the Octicons icon `mark-github`, single colour black | `assets/github-mark.svg` | Octicons: MIT, "Copyright (c) 2026 GitHub Inc." ([LICENSE](https://github.com/primer/octicons/blob/main/LICENSE); the README: "Code License: MIT, applies to all other files", "When using the GitHub logos, be sure to follow the GitHub logo guidelines"). [GitHub logo guidelines](https://brand.github.com/foundations/logo): linking to GitHub or a project on GitHub with a permitted logo is allowed; forbidden are use as one's own logo, implying endorsement and modification (colour, dimensions); allowed colours are white and black. The skill uses the mark unchanged (same path data, scaled in proportion, black or white), smaller than and next to the project name, only to link to the repository. | **confirmed** (LICENSE, README and guidelines page read on 2026-10-29) |

## Repository only (website and README images, not part of the `.skill`)

| Component | Where | Licence | Status |
|---|---|---|---|
| IBM Plex Sans, Sans Condensed (website fonts, WOFF2, self-hosted, no Google request) | `docs/fonts/` | SIL Open Font License 1.1, Copyright © 2017 IBM Corp., Reserved Font Name "Plex"; licence text in `docs/fonts/OFL-IBMPlexSans.txt`; WOFF2 files from the npm package `@fontsource/ibm-plex-sans` | **confirmed** (`docs/fonts/OFL-IBMPlexSans.txt`) |
| EU label copies for the website footer and the README footers: `ai-basic.svg` (black, from the working copy above) and `ai-basic-dark.svg` (white, built from the official white file of `assets/eu-labels/`, same crop, styles inlined) | `docs/img/` | as above | **confirmed** |
| GitHub mark copies for the Markdown footers: `github-mark.svg` (black) and `github-mark-dark.svg` (white), built from the skill asset above | `docs/img/` | as above | **confirmed** |


## Used at run time (installed by `scripts/setup.sh`, not bundled)

| Component | Use | Licence | Status |
|---|---|---|---|
| Verovio 6.3 | score engraving | LGPL-3.0 ([licensing page](https://book.verovio.org/introduction/licensing.html)). **Condition: visible credit to Verovio** – the README of every package says "engraved with Verovio (verovio.org)". Changes to Verovio itself would have to be published under LGPL-3.0; the skill does not modify it. | **confirmed** |
| Leland (music font inside Verovio) | notation glyphs in the score PDFs | SIL Open Font License 1.1 ([upstream](https://github.com/gameleaf/Leland)); embedding in PDFs is allowed | **confirmed** (upstream page); copyright holder not named there |
| MuseScore General (soundfont) | sound of the practice audio | MIT, parts public domain or CC0 (Debian copyright file of the package `musescore-general-soundfont`); the soundfont is a sample bank, the MuseScore program is not used | **confirmed** (package copyright file); the audio rendered with it is not a copy of the soundfont |
| FluidR3_GM (fallback soundfont) | same | MIT, Copyright © 2000-2002, 2008 Frank Wen (Debian copyright file of `fluid-soundfont-gm`) | **confirmed** |
| chorMaleFem (optional soundfont, added by the user, not shipped) | choir sound of the practice audio (`make_audio.py --choir-soundfont`) | Polyphone lists it as "public domain" (uploader "bottrop", [page 661](https://www.polyphone.io/en/soundfonts/vocals/661-chormalefem)); the file itself carries no author or licence data. The preset names point to Papelmedia ("ChorMalePapl") and KBH ("ChorFemKbh"); the original Papelmedia choir soundfont is listed on Polyphone as "give credit" (author Simon Tristan Papel, [page 227](https://www.polyphone.io/en/soundfonts/vocals/227-papelmedia-final-sf2-xxl-aaa-choir)). A byte comparison with the Papelmedia and KBH originals found no copy; a correlation check was inconclusive | **to check** |
| VocalsPapel (optional soundfont, added by the user, not shipped) | choir sound of the practice audio (same option) | Polyphone lists it as "public domain" (uploader "bottrop", [page 662](https://www.polyphone.io/en/soundfonts/vocals/662-papelmedia-vocals-solo)); the file carries no author or licence data. The presets are named after the singers Irina Brochin, Rudolf Krupp and Pavel Brochin and carry the Papelmedia name; the rights of the singers and of Papelmedia are unclear, so "public domain" is doubtful | **to check** |
| CairoSVG | SVG to PDF | LGPL-3.0-or-later | **confirmed** (package metadata) |
| lxml, pypdf | XML, PDF | BSD-3-Clause | **confirmed** (package metadata) |
| mido | MIDI | MIT | **confirmed** (package metadata) |
| ReportLab | PDF documents | BSD | **confirmed** (package metadata) |
| Pillow | images | MIT-CMU | **confirmed** (package metadata) |
| NumPy | audio analysis | BSD-3-Clause and others (0BSD, MIT, Zlib, CC0) | **confirmed** (package metadata) |
| SciPy | signal processing | BSD-style | **confirmed** (package metadata, licence text not read) |
| poppler-utils (`pdftoppm`) | PDF pages to images | GPL-2 or GPL-3 for the core library, Poppler's own contributions GPL-2-or-later (copyright file of the Debian package `poppler-utils` 24.02.0, read on 2026-10-29) | **confirmed** |
| fonts-dejavu-core (DejaVu Sans) | only for the debug images of `preflight.py`; not in any package | Bitstream Vera licence (copyright file of `fonts-dejavu-core` 2.37, read on 2026-10-29): use, copying and redistribution allowed, keep the notice, modified fonts must be renamed, the fonts may not be sold alone; DejaVu's own changes are public domain | **confirmed** |
| FluidSynth 2.3 | MIDI to audio | LGPL-2.1 (upstream [LICENSE](https://github.com/FluidSynth/fluidsynth/blob/v2.3.0/LICENSE) at tag v2.3.0, "Version 2.1, February 1999", read on 2026-10-29) | **confirmed** |
| FFmpeg (with LAME) | audio mixing, MP3 encoding | the build used here is GPL-enabled (`--enable-gpl`, libmp3lame); applies to the programs, not to files made with them | **confirmed**: Debian copyright file of `ffmpeg` 6.1.1 (read on 2026-10-29): the default Debian binaries are GPL-2-or-later because GPL parts are built in; `libmp3lame0` (LAME) is LGPL-2-or-later. Duties (source offer) arise only for whoever redistributes these programs, not for the skill, which ships none |

None of the run-time components is shipped in the skill or in a package, so their licences create no duties for users of the skill beyond the Verovio credit; they matter only if someone redistributes these programs.

## Output of the skill

Packages contain the engraved score, audio and documents derived from the user's source. The rights to the music, text and source stay with the rights holders. The skill grants no rights and gives no legal advice (see the "Rights" section of each package's README).

## Licence of the skill itself

PolyForm Noncommercial License 1.0.0 (SPDX `PolyForm-Noncommercial-1.0.0`, see `LICENSE.md`, unmodified official text): free for any noncommercial purpose (personal use, hobby, charitable, educational, public bodies); commercial use needs a separate licence from the author. No author name is given on purpose, so there is no `Required Notice` line. The licences of the bundled assets above stay as stated and are not changed by this licence.
