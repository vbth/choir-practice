---
name: choir-practice
description: Turn a choir score PDF (scan, photo or notation-software export) into a complete, ready-to-share practice package – one ZIP with practice audio and MIDI per voice in three stages (solo, with accompaniment, in the choir) plus tutti, each in choir and piano sound, an overview PDF, a bilingual README, check log, correction log, session handoff – with one complete, individually zippable folder per voice (guide, practice MP3s) and a guide for the choir director. Use this whenever someone uploads a choir/vocal score and wants parts, rehearsal tracks, practice MP3s, "Übe-Dateien", "Stimmen zum Üben", "Probenaufnahmen", single-voice scores, or a "Chorpaket" / "Chor-Übungsmaterial" – even if they only say "mach mir daraus Übematerial" or "split this into voices". One score in, one checked, ready-to-share rehearsal package out – you approve every decision. Audio is mechanical and note-exact, not an interpretation.
---

# Choir practice material

The user supplies **only a PDF** of a choral piece. You deliver **one finished ZIP** containing scores, practice audio and documentation. The work is long and error-prone in exactly one place – reading the music correctly – so the workflow is built around gates: no phase starts before the previous gate has passed, and every check is logged.

Display name for users: `skill_name` in the language pack (de: "Chor-Übungsmaterial", en: "Choir practice material") – use it in the user's language whenever the skill is named in user-facing text (README, final message).

## First step, always
**Before any other work – in every new chat, after installing or updating this skill, after a session handoff, and before rerunning any single script (e.g. only make_layout.py or make_docs.py) – run `bash <skill dir>/scripts/setup.sh --check`.** It installs nothing and reports what is present, what is missing and how the installed Python packages differ from the tested versions in `scripts/requirements-stable.txt`. A fresh environment has none of the audio and notation tools; working without them silently skips or fakes steps (no audio rendering, untestable timing).

- **Nothing missing, all tools ok:** continue (for the first run in a chat: `setup.sh --stable` once, a no-op when the versions match) and go on with Stop A. Before a rerun of a single script, `--check` alone is enough.
- **Something missing or different (`python state: missing|differs`, or apt packages to install) – this comes before Stop A and is a hard stop:** tell the user in 3–6 short lines what will be installed (apt packages; Python packages with tested vs. installed version) and ask once with `AskUserQuestion`: **tested stable versions (Recommended)** or **newest versions** (the free-text field stays available). Then run `setup.sh --stable` or `--latest` and wait until every tool is ok. The question is asked in the user's language; log it like a stop (`question_asked` / `answer_received`, phase 0).
- **Unattended** (user away, scheduled run): take the stable versions without asking.
- **Always log the result:** `python3 $S/log_check.py $WORK 0 setup_versions pass "<mode, versions line from the report>"`. With `--latest` log `warn` and the note "newest versions, not tested", and say so in the final message.
- If the stable versions cannot be installed (no ready-made package for this Python, no network), say so, offer the newest versions as the alternative (ask, never switch silently) and log it.
- If setup cannot install something else, say exactly what is missing and what that means for the result before continuing.
- **Third-party rights check (mandatory, part of the installation):** `setup.sh` ends with `check_third_party.py --brief`; run `python3 <skill dir>/scripts/check_third_party.py` once per chat and log it (`log_check.py $WORK 0 third_party pass|fail "<result line>"`). It lists what is bundled in the skill, what lives only in the repository and what is installed at run time, and fails when a component is not named in `THIRD_PARTY_NOTICES.md`. On `fail` tell the user which components are missing from the notices; the work may continue, the gap goes into the final message.

## Deliverables (folder names come from `delivery` in the language pack)

The work package built in phases 5–7 (raw layout, checked by `verify.py`) is **not** what the user gets. `package.py` calls `make_layout.py`, which builds the delivery layout and the ONE ZIP:

```
<YYYY-MM-DD>_Chor_Uebungen_<Title>.zip   date first (sorts chronologically); the ZIP holds the numbered folders directly:
  1_Noten/         1_Noten_<T>_Scan.pdf (the supplied original)  2_Noten_<T>.pdf  3/4_MusicXML_<T>_<Chor|Klavier>
                    5_MIDI_<T>/<voice>_MIDI_<T>/ 1_<voice>_<T>_<Chor|Klavier>_<content>.mid …  and  Tutti_MIDI_<T>/
  2_Ueben/         1_Uebersicht.pdf  2_Anleitung.pdf (guide for the director; generic, no piece title; en `1_Overview.pdf`, `2_Guide.pdf`)  and one ZIP per voice:
                    <abbr>_Ueben_<T>.zip   complete on its own, unzips to the folder <abbr>_Ueben_<T>/ (package.py zips it after the self-check)
                    1_<abbr>_Anleitung.pdf (generic: heading only "Übe-Dateien für <voice>")  2_<abbr>_Noten_<T>.pdf (the same full score in every voice ZIP)
                    3_<abbr>_Audio_Chorklang_<T>/    1_<abbr>_<T>_Chor_allein_langsam.mp3 … 6_<abbr>_<T>_Chor_alle_Stimmen_gleich_laut.mp3
                    4_<abbr>_Audio_Klavierklang_<T>/ same names, _Klavier_
  3_Dokumentation/ 1_README  2_Pruefprotokoll  3_Korrekturprotokoll  4_Session_Handoff (+ .md/.pdf)
  4_Werkzeuge/     1_Projektdaten_<T>/ (score.json, docs.json, mixes.json, layout.json; the scripts live only inside the skill)
                    2_SKILL_<skill with underscores>_v<version>/ (<skill with underscores>.skill, README.md, session_handoff.md)
```

Rules of the layout (checked by `make_layout.py`, which exits 1 on a violation):
- **Numbers without gaps** in every folder; the top level is 01–04. At most **3 folder levels** below the root.
- **Folder names say what is inside (always):** sub-folders carry type and title, not just a code – e.g. `B1_MIDI_<T>`, `Tutti_MIDI_<T>`, `B1_Ueben_<T>`, `3_B1_Audio_Chorklang_<T>`.
- **Underscore only (always):** no hyphen in any file or folder name of the package – words inside a name are separated by `_` too (`mit_Melodie_langsam`, `Session_Handoff`, skill folder `choir_practice`); `common.safe` turns hyphens in titles into `_`, and `make_layout.py` fails on any hyphen outside `scripts/`. Only the skill's own identifier (`choir-practice`, in the standalone `.skill` file and SKILL.md) stays kebab-case.
- **No AI mark in file names (always):** file and folder names carry no `KI`/`AI` suffix or infix (e.g. `1_B1_<T>_Chor_allein_langsam.mp3`, `1_B1_Anleitung_<T>.pdf`, ZIP `<date>_Chor_Uebungen_<Title>.zip`). The AI labelling lives inside the files (footer, EU label, metadata, see "AI nomenclature"), not in the names. The supplied scan stays `1_Noten_<T>_Scan.pdf`.
- **Number, voice, title, sound, content** in this order; a number is always followed by an underscore, never a hyphen (`<n>_<abbr>_<T>_<Chor|Klavier>_<content>`); content words follow the language's capitalisation (German: nouns capitalised, e.g. `mit_Melodie_langsam`, `eigene_Stimme_lauter`; list `capitalised_nouns` in the language pack, checked). Inside `2_Ueben` (voice folders) every file and folder name carries the voice abbreviation right after the number (guide, score, audio folders, MP3s); the self-check fails otherwise.
- **Stages 1–6 are the same everywhere:** 1 solo slow, 2 solo, 3 with melody slow, 4 with melody, 5 own voice louder, 6 tutti (all voices equal). For the melody voice 3/4 are called "with piano".
- **No file is stored twice** (checked by hash) except what makes a voice ZIP complete: guide, score (the same full score, no highlighting) and the tutti (stage 6) in each voice ZIP. MIDI lives only in `1_Noten/5_MIDI_<T>` (stages 1–5 per voice, tutti separately).
- **Score in the voice ZIPs:** an unchanged copy of `1_Noten/2_Noten_<T>` – one PDF is engraved and copied into every voice ZIP; no per-voice rendering.
- **MP3 tags on every MP3:** title "<Title> – <n> <label>" (the piece title is part of it, because players show the title first), album "<Title> <Voice>, <Chorklang|Klavierklang>" (so choir and piano versions never collide in a player), track n/6, artist = composer, date = year, comment and copyright = AI nomenclature (see above).
- **Album art on every MP3 (always, same cover for every voice of a piece):** `make_cover.py` (called by `make_layout.py`) paints one square cover (600 × 600, JPEG, embedded as front cover) from the music, deterministic: hue from the key signature (circle of fifths, 30° per step, hue = 120 + 30 × fifths, so C major = green and enharmonic keys match), lightness from the register (mean pitch, ±0.06), minor = darker and cooler, tempo = softness of the radial transitions (slow = soft), metre = position of the dark centre. Four radial colour fields, no linear gradient, a little grain. Text: piece title (IBM Plex Sans bold, top left) and the EU label "AI GENERATED" alone, without words next to it (bottom right, height 9 % of the cover, margin 5 %, fixed in `make_cover.py` as `LABEL_H` and `LABEL_MARGIN`), always black. Legibility is enforced on the pixels: title box and label (the black pill must stay recognisable) reach contrast ≥ 7:1 with black, otherwise a light feathered zone is blended in behind them just as strong as needed. The self-check fails for an MP3 without cover; a failed legibility check is a warning in the build output and `fail` in the check log (`cover_art`). The cover shows no third-party image.
- **Voice abbreviations** from `voices[].abbr`, otherwise first letter + digits of the name (T1, B2, S, A). Set `abbr` whenever two voices would collide (e.g. Bariton/Bass).
- The guide texts come from `share` in the language pack; keep them short, concrete and addressed to the singer ("du"/"you").

**Consistency rules (one fact, one wording – applied where it is produced, checked in `make_layout.py` unless noted):**

| Rule | Applied in | Checked |
|---|---|---|
| One vocabulary for the six practice files: display name = file-name part (`mit_Melodie_langsam` → "Mit Melodie langsam"); the names in guides, director guide, MP3 titles and file names are identical; stage numbers (Nr. 1–6) and stage names (Solo, Mit Begleitung, Im Chor, Tutti) are explained together in README and overview | `delivery.fname` in the language pack is the single source; `share.items` must match it | display name vs file name; guides contain every name |
| Every MP3 carries the piece's album art, text legible | `make_cover.py`, `make_layout.py` | cover embedded in every MP3, contrast ≥ 7:1 on title and label (check `cover_art`) |
| Choir and piano versions are distinguishable in a player | MP3 album "<Title> <Voice>, <Chorklang\|Klavierklang>" | album + title unique over all MP3s |
| Every PDF has its own title ("<Title> – <document>[ <voice>]") | PDF metadata step | titles unique |
| Credits read the same everywhere: order Text, then Musik (Lyrics, Music); pattern "Name (Text), Name (Musik)" in the score header, the MusicXML credits and the cover | `build_score.py`, `render_score.py`, language pack `cover` | MusicXML credits; header test by looking at the page |
| Software/creator metadata carries the skill version | `build_score.py`, metadata step | MusicXML `<software>` |
| Names are written in the language's orthography (German nouns capitalised) | `capitalised_nouns` | file and folder names |
| Texts mention only folders that exist, no removed formats (MuseScore) | language pack, docs.json | folder tokens `NN_Name` in every document |
| Shared documents (README, logs, handoff) are neutral – no "du/you"; only the singer guides address the singer; quotes from the lyrics are exempt | language pack, docs.json | pattern check outside quotes |
| The session handoff states current facts only | tokens (see Phase 7) | package name, version, date, folders |
| The check log shows each check once (latest run), in the user's language | `make_docs.py` (`protocol_notes` in the language pack) | no duplicate rows |
| Rights status is recorded and shown | Phase 2 gate, `rights` in `score.json`, README section | status present, README section present |
| Development history is not shipped: the CHANGELOG entry and the skill handoff of the version being released contain only what is new in that release | `release.py` | by hand before release |

Practice stages (levels relative to the own voice, own voice always centred):
1. **Solo** – own voice only.
2. **With accompaniment** – own voice, melody voice −4 dB, soft piano accompaniment of all voices −12 dB (melody singers: own voice + accompaniment). The accompaniment is piano in both sound versions.
3. **In the choir** – real seating: neighbours left/right −7 dB, edge voices get the next-but-one voice on the free side −9 dB, others far out −12 dB. Both ears always filled.
Every audio file exists in **choir sound and optimised piano (legato)**, as MP3 and MIDI; stages 1–2 also **slow (default 75 %, adjustable with `make_audio.py --slow-pct N`, 10 to 95; the value goes into `mixes.json` and the README)**. Each voice file starts with the own starting note (2.0 s long), a pause of 3.0 s, then straight into the music (2.0 s pause between the verses); tutti files start with every voice's starting note one after another (low to high) (no count-in; `COUNT_IN` in make_audio.py brings it back). Loudness −19 LUFS, MuseScore General soundfont, light reverb. Rationale and defaults: `references/musical-defaults.md`.

## Language

- Talk to the user, ask questions, and produce every user-facing file (PDF texts, folder and file names, logs) in **the user's language**. The skill's own instructions and scripts stay English.
- Language packs: `assets/i18n/<lang>.json` (de, en included). For another language, copy `en.json`, translate every value (keep keys, keep names ASCII-safe for folders), show the user the folder/stage names for a quick OK, save it, then continue.
- README: user language + English (English users: English only). session-handoff.md: always English.
- Set `"language": "<lang>"` in score.json – all scripts read it.
- **The language is decided, not detected:** the user's language is the language the user writes in (the conversation) – not the language of the score or its lyrics, which can differ (a German choir may sing English lyrics). No detection library; English users get a fully English package (names, PDFs, logs, README in English only). State the choice in one line in the workflow overview ("Sprache der Dokumente: Deutsch, README zusätzlich Englisch") so it can be corrected before anything is built. Unclear or mixed → English. No pack for the language → create it from `en.json` as above and use English until the user has confirmed the folder and stage names. The lyrics language only matters for syllable and hyphen handling, never for the documents.

## Second step: show the workflow, then Stop A

Right after setup, and before any analysis, show the user the rough workflow in 6–8 short lines (survey and preflight check → approval of work details → transcription → proofreading twice → score → audio → documentation, ZIP), the language choice in one line (see Language) and where you will stop and ask (Stops A, B and, only if needed, C below; the installation question comes before Stop A and only if something is missing or different). The same message names the expected effort once known. Then ask Stop A. **Stop A comes before the score is uploaded:** if the skill is called without a score, run Stop A first and ask for the score afterwards (the user can then decide not to upload). If a score is attached to the call anyway, do not open or analyse it before Stop A is answered.

## Question plan (what is asked when, so there are no detours)

The skill asks in **stops**. A stop is one point in the process where all questions of one topic group are asked together and nothing else runs; how many tool calls it takes is a technical detail (`AskUserQuestion` takes at most 4 questions per call: send consecutive calls back to back, grouped by topic, with no work in between).

Principles:
1. **Ask only what the score, the web or a rule cannot answer.** Read, search and measure first; a question must never ask for something already visible in the source.
2. **Order by dependency.** A question whose answer can make later work pointless goes first (rights and intended use, scan quality). Questions that need findings come after the survey. Everything the user can know before any analysis is asked at the first stop, everything that depends on the score at the second – no third round for things that were known earlier.
3. **One batch per stop, no drip-feeding.** Collect what comes up and ask it together. Only blockers (unreadable scan, a missing tool) interrupt at once.
4. **Every question serves the process:** it says what it decides, offers 2–4 concrete options built from the findings, puts the recommended option first with the reason, and always allows "you decide" (the proposal is then used and marked as such). Each answer is written to `score.json` / `docs.json` and logged.
5. **No question after the approval of the work details except Stop C.** Phases 5–7 use the defaults of this skill; deviations go into the README open points and the final message.

| Stop | When | Asks | Decides | Written to |
|---|---|---|---|---|
| **0 – Installation** | right after `setup.sh --check`, only if something is missing or differs | tested stable versions (recommended) or newest versions of the Python packages; the apt packages are listed, not chosen | what `setup.sh` installs | check log `setup_versions` |
| **A – Intake** | after setup, before any analysis | **Rights and use:** status of the source (four options, `unclear` is an explicit option: public domain / licence or permission exists / own work or rights held by the client / unclear), intended use (rehearsal in the own choir – listed first and the default / commercial); for a licence a reference (publisher, collecting society, licence number); a © line printed in the source is transcribed, never dropped. Commercial use with `unclear` (or `licensed` without reference) is not blocked, but gets a clear warning: once at Stop A, in the README rights section, as `warn` in the check log and in the final message. Language only if no language pack exists (see Language) | whether the work makes sense at all; README section "Rechte"/"Rights" | `rights` in `score.json` (`status`, `use`, `reference`, `note`, `notice`) |
| (blocker) | during the survey | scan quality ABORT: better scan or continue without that page | whether transcription can start | – |
| **B – Work details** | after survey and preflight, before transcription | in one batch: (1) work details table (title, subtitle, composer, arranger, lyricist with sources; approve / correct), (2) melody voice (proposal + reason), (3) seating, (4) tempo, (5) only if found: playback order for repeats, endings, re-entries, divisi, (6) only if unclear: which voices or verses a performance hint applies to, (7) only if unclear: which pages or pieces of a multi-page file belong to this job | everything Phase 3 builds on | `score.json`, `docs.json` (`meta_sources[].approved`) |
| **C – Open points** | end of Phase 4, before the score and audio are made | only if proofreading left spots that cannot be settled from the source: all of them together, each with bar, voice, crop and options (reading A / reading B / "as in the source, flag it") | the notes that go into score and audio | `score.json`, correction log |

Interaction rules:
- **Questions and approvals go through `AskUserQuestion`** (chat interface) whenever the tool exists: 2–4 concrete options each, the recommended option first with "(Recommended)", reasons in the option descriptions. The tool always offers a free-text field ("Other"); never add a fake "Other" option. Only if the tool is missing, ask in plain text with numbered options.
- **A stop is a hard stop.** After asking, do nothing else: no transcription, no audio, no background jobs, no further tool calls except reading what is needed to understand the answer. Resume only with the answer. Start no long job (audio, rendering) while any question is open, and stop running jobs if a question arises that can change their input.
- **Unattended exception.** Only when the user said they are away or the session was started by a schedule: take the best-supported values, mark them "not confirmed" in README, session handoff and final message, and carry on. A question that went unanswered in a live chat is not "away". Exception to the exception: an unanswered rights question is never assumed – the status is recorded as `unclear`.
- **Log every stop:** `python3 $S/log_check.py $WORK <phase> question_asked manual "<topic>"` right before the first `AskUserQuestion` of the stop and `… answer_received manual "<topic: answer>"` right after the last one, so the statistics can show waiting time separately (the check log keeps one row per stop).

## Ground rules

1. **Never guess.** If a note, rhythm, syllable or marking cannot be read with certainty, transcribe the most likely reading, mark it `uncertain` in docs.json corrections, and name it in the README's open points. Never fill gaps silently.
2. **Gates.** Each phase ends with a gate. A failed gate → fix the cause and re-run the gate; at most **3 rounds**, then stop and explain the situation to the user (what fails, why, options).
3. **Log everything.** Scripts log themselves when given `--workdir WORK`; manual checks (proofreading passes, approvals) go in with `scripts/log_check.py`.
4. **Only claim what was checked.** Audio was not listened to by you like a person – it was tested technically against the MIDI (audio test); say so, and never claim anything about sound quality or musical taste. Proofreading results are reported as what was compared, not as certainty.
5. **The source is the reference.** Keep its spelling, hyphenation, bar numbering and verse order. Deviations (e.g. obvious engraving errors in the source) are allowed only with a correction-log entry and a visible note to the user.
6. **Readability beats page count.** Staff space ≥ 1.6 mm (scale ≥ 90) is a hard limit; use more pages rather than smaller music; every page filled vertically; footer on every page (see "Design of all PDFs").
7. **Wrong assumptions are caught early.** Phase 1 ends with the preflight check; nothing is announced to the user, no score.json is written and no melody voice is named before it passed.
8. **Gates stop.** See "How to talk to the user": an open question stops all work.

## Documents (all PDFs)
- **Design of all PDFs (Swiss style, always):** one font family, **IBM Plex Sans** (SIL OFL, `assets/fonts/`, `common.register_plex()`), flush left on one **20 mm text axis** (text, tables, footer, music all start on it), **100 % black**, no fills, generous white space. **No colour at all, no signal colour:** `ACCENT` in `common.py` is black; table heads are bold with a black rule under them, the own voice in the overview is a solid black dot with white letters. **Tables have thin black lines on all cells** (columns and rows), the table's left edge sits on the text axis. Score notation: **Leland** (Verovio `font`) with Verovio's standard line widths (`staffLineWidth` 0.15, `stemWidth` 0.20, `barLineWidth` 0.30; env `SCORE_LINES` overrides, env `SCORE_MUSIC_FONT` the notation font); lyrics, tempo word and bar numbers in **IBM Plex Sans Condensed** (same family, width 85 – the regular width made syllables collide because Verovio plans the spacing with narrow text), lyric size 3.8, lyric line height factor 1.3 (`lyricHeightFactor`) so the verse lines do not crowd, thin hyphen/underscore lines (`lyricLineThickness` 0.10), staff spacing 14 / system spacing 18.
- **One footer on every PDF, identical (always):** flush left `[EU label AI] KI-generiert, Urheber- und Lizenzrechte ohne Gewähr, DD.MM.YYYY` (no title, no dashes), page number flush right (exception: on the music pages the page number is in the header line, flush right), IBM Plex Sans, 100 % black, **8 pt on every PDF** (`common.FOOT_PT`; the EU label "AI" (the basic label, no GENERATED / MODIFIED) is sized so that its capitals match the cap height of the text, on one baseline). The cover page has the same footer without a page number. The Markdown files end with the same line: one blank line before and one after it, with `[EU label] KI-generiert, Urheber- und Lizenzrechte ohne Gewähr, DD.MM.YYYY` (English: `AI-generated, no guarantee for copyright and licence rights, YYYY-MM-DD`; label linked from the repo, see `common.md_footer`). Never a middle dot `·`; the phrase itself uses a comma. No mention of transcription or correction. Code: `common.rl_footer` (reportlab PDFs, cover), `add_footer` in render_score.py, `make_overview.py`, `common.md_footer`. Only the supplied scan carries no footer.
- **AI nomenclature (exact, always, bilingual – language pack keys `ai_tag`, `ai_meta`, `ai_note_info`):** the package language selects the column; the strings are never paraphrased and never mention "transkribiert", "korrigiert" or "KI-Unterstützung":

  | | de | en |
  |---|---|---|
  | `<tag>` | `KI-generiert` | `AI-generated` |
  | `<long>` | `KI-generiert, Urheber- und Lizenzrechte ohne Gewähr` | `AI-generated, no guarantee for copyright and licence rights` |

  | Where | Exact content |
  |---|---|
  | Footer of every PDF | `[EU label AI] <long>, DD.MM.YYYY` (no title, no middle dot), 8 pt, page number right (music pages: page number flush right in the header line instead) |
  | PDF metadata | Title `<Title>`, Author / Creator / Producer / Keywords `<tag>`, Subject `<long>` (not on the scan) |
  | MP3 (ID3) | title `<Title> – <n> <label>`, album `<Title> <Voice>, <Chorklang\|Klavierklang>`, track n/6, artist = composer, date = year, comment and copyright `<long>` |
  | MusicXML | `<rights>` and `<encoding-description>` `<long>`, `<encoding-date>` = delivery date |
  | MIDI | meta events `copyright` and `text` `<long>` at tick 0 of the first track |
  | README / logs (.md) | after the end of the text **one blank line**, then the single line `[EU label] <long>, DD.MM.YYYY`, then one more blank line (`common.md_footer`: the label is linked from the repo, black, white in dark mode; commas, no middle dot; not in the handoff). The repo READMEs end the same way in their language; `release.py` sets the date, `check_templates.py` checks it |

  How the notes were made (AI transcription, two proofreading rounds, human approval, software-synthesised sound) is explained only in the README section "Hinweis zur Entstehung". **After every build `make_layout.py` checks all of this in its self-check** (PDF/MP3/MusicXML/MIDI/Markdown metadata) and exits 1 on any miss – never deliver a ZIP that did not pass. The EU label is drawn by `common.icon_markup` / `rl_footer`; labels `assets/eu-ai-basic.svg` ("AI", the official round basic icon: every PDF and Markdown footer), `eu-ai-generated.svg` ("AI GENERATED": album art, header image and website footer) and `eu-ai-modified.svg` (kept for another policy); these are cropped working copies of the official set, which lies unchanged in `assets/eu-labels/` (12 SVG: black, white, 50 % transparent).
- **Voice labels in the printed score:** abbreviations (T1, T2, B1, B2) in every system, also the first; full names appear in the guides, README and file metadata only.
- **Score cover page (template, always identical):** the score PDF starts with a cover page, Swiss style: flush left on the 20 mm axis, IBM Plex Sans, 100 % black, no rule, no document-type label, no date. The title in bold (30 pt, tracking −0.015 em, shrinks only if too wide), then a label/value grid with **Musik and Text only** (labels in the language pack `cover`), and at the bottom the footer above without a page number. Built by `make_cover` in `render_score.py` from score.json (`--spec`); layout.json has `cover: true`, `pages` counts the music pages only; page numbering: cover = 1, first music page = 2.
- **Music pages carry one header line (always):** flush left on the 20 mm axis, same size as the lyrics, IBM Plex Sans: **Title** (bold), then `, Name(s) (Text), Name(s) (Musik)` (regular; several names comma separated; English `(Lyrics)`, `(Music)`), the **page number flush right on the same line**. Code: `header_parts`/`add_header` in render_score.py (Verovio's own `header` stays `none`, top margin 20 mm, header baseline 12 mm). Every music page also carries the footer above.
- **Margins:** music pages 20 mm left and right (the text axis), 10 mm top; the footer baseline sits 11.2 mm above the page edge (reportlab PDFs 12 mm) and the music ends 27 mm above it, so about 12 mm stay clear between the last lyric line and the footer. Every other PDF: 20 mm on all sides.
- **Overview PDF:** no sound/tempo/loudness line under the diagrams – nothing but title, stages and the footer.
- No copyright or legal boilerplate in the documents.

## Workflow

Use a task list with one task per phase. Work directory: `WORK=<scratch>/<slug>`; package folder `PKG=$WORK/pkg`. `S=<skill dir>/scripts`.

### Phase 0 – Setup (gate: all tools ok)
Mandatory, see "First step, always". `bash $S/setup.sh --check`, the package question if needed, then `bash $S/setup.sh --stable|--latest` → must report python, fluidsynth, ffmpeg, pdftoppm, soundfont ok. Soundfont fallback → log + tell user. `python3 $S/log_check.py $WORK 0 setup pass "<summary>"` and `… 0 setup_versions …` (see "First step, always").

### Phase 1 – Survey (after Stop A; gate: structure understood, scope announced)
0. Source as image file(s) (photo, scan as JPG/PNG/TIFF/WebP): `python3 $S/scan_tools.py topdf img1 [img2 …] source.pdf` first; this PDF is the source from here on (and the delivered "Scan"). A MusicXML file from notation software is a draft only (Phase 3).
0b. Compare the first page (composer, lyricist, arranger, year, edition, any © line) with the rights answer of Stop A. A contradiction (for example "public domain" for a living composer or a © line) is stated in one line in the Stop B table and set in the README rights section; the answer is never changed silently.
1. `python3 $S/scan_tools.py extract source.pdf $WORK/pages` → page PNGs, text layer (OCR text of scans is unreliable – use it only as a hint for lyrics).
2. Per page: `scan_tools.py staves page-N.png --out $WORK/staves-N.json`, then `scan_tools.py crops page-N.png staves-N.json $WORK/crops --per-system <staves per system> [--guides --clefs treble8,bass]` and look at every crop with Read.
3. **Preflight (mandatory, before anything is announced):** `python3 $S/preflight.py page-N.png --out $WORK/pre-N --clefs <clef per staff, e.g. treble8,bass,...> --key <fifths> [--per-system 2]`. It fits the five staff lines locally (tilted, curved or handwritten pages), measures every note head against its local lines, reports stem directions per staff and writes crops `grid_*.png`. **Scan quality is a hard abort criterion:** the tool prints `SCAN QUALITY` and exits with code 3 and `VERDICT: ABORT` when staves are missing, staff space < 8 px, contrast < 40, staff count differs between windows (< 60 % agreement) or > 50 % of the heads are off-centre. On ABORT stop at once: ask with `AskUserQuestion` for a better scan or photo (flat, sharp, even light, ≥ 150 dpi) or, for a multi-page file, whether to continue without that page; transcribe nothing from the failed page. `WARN` lines (staff space < 12 px, > 25 % off-centre heads) go into the first message to the user and raise the uncertain-spot expectation. Then check, in this order, and fix the survey where it disagrees:
   a. Staves counted by you on the page image = staves the tool found (otherwise use the local fit only).
   b. Voices: staves × voices per staff. Stems up and down on one staff = two voices. Name them (S1, A1, T1, T2, B1, B2 …).
   c. Rhythm per voice inside one bar (a voice may have other note values than its partner); a bar sum off by one eighth means a voice was merged into a chord.
   d. Pitch from measured head positions, not by eye; ties vs. slurs by pitch; accidentals within the bar.
   e. Bar structure: pickup, short bar at a system end plus the missing part at the next system start = one bar.
   f. Lyrics aligned by x position; melisma is not a missing syllable.
   g. Handwriting (circled letters, pencil tempo, fingerings) → open points, never music.
   h. Melody voice: never from a default rule. Transcribe the first phrase of each voice, compare the contour with the known tune (web search if unsure), then propose with the reason.
   j. **Performance hints** (look for them actively): printed texts about execution (e.g. a verse louder/softer, tempo words, rit., breath marks), dynamics (pp to ff, sf), hairpins `<` `>` (start bar and end bar, also over several bars), fermatas, accents, per-voice differences. List them per bar and voice, ask when unclear which voices or verses they apply to, and enter them as `directions` (and `repeats` / `playback` for structure). Hints that apply to a verse or a pass rather than to bars are written as `performance_notes` (shown on the cover page of the score with bar and page of the place, if given) and, in the README, as notes. Only remarks that are printed in the source belong there; add each as `{"text", "bar"}`.
   i. **Structure and re-entries** (look for it actively, it changes audio and documents): repeat signs, 1st/2nd endings (voltas), D.C./D.S./coda, verses sung over the same music, voices that enter at another bar in a later verse or after a repeat (bridge, interlude, different last verse), divisi inside a staff, optional or ossia bars. List each as source bar → what happens. If anything of this exists and the playback order is not completely clear from the score, ask at Stop B (see the question plan) – never guess an order.
   Accidentals and rhythm are not measured by the tool – they are read by you from the crops.
4. Determine: voices (also several voices on one staff, divisi), clefs, key, time signature and changes, pickup, number of bars and source bar numbering, verses/refrain structure, repeats/voltas/D.C., voice-specific lyric lines, dynamics, tempo marking, title block, piano accompaniment (if any).
5. Tell the user in 3–5 lines what you found and the expected effort (pages, bars, verses). Long works: transcribe in sections and show interim states.
Gate: log `1 survey pass`.

### Phase 2 – Stop B: approval of the work details (hard stop)
- Title, subtitle, composer, arranger, lyricist: read them from the source. If anything is missing, abbreviated, cut off or ambiguous, **search the web** (catalogues of choral music, publisher pages, library catalogues, Wikipedia/IMSLP/CPDL). Prefer primary sources.
- Also propose: **melody voice** (usually the top voice unless the melody clearly lies elsewhere), **seating** left→right (defaults in musical-defaults.md), **tempo** (from the marking, table in musical-defaults.md).
- Show one compact table (item · value · source link · confidence), then ask the whole batch of Stop B (see the question plan): work details, melody, seating, tempo and, only where the survey found them, the playback order for audio and MIDI (options: as printed once / your reading with the order written out / other), the scope of a multi-page file, and the reach of performance hints. Signs go into `score.json` as `repeats` (engraved and played) and everything else as `playback` (see `references/score-spec.md`); the played order is stated in the README. **Then stop and wait.** No transcription, no audio, no background job until the answer is in. (Reading the source again to prepare the next phase is fine; writing score.json is not.)
- Rights were settled at Stop A. Never drop a printed © notice; the skill does not check or grant rights and gives no legal advice. The README gets a neutral section "Rechte"/"Rights" (clear "do not pass on before cleared" when `unclear`); in the final message say the status in one line and, for `unclear`, warn once. `make_layout.py` fails without a rights status; commercial use with open rights only prints a warning (never blocks).
- Approved → `meta_sources[].approved = true` in docs.json. No answer (user away) → use the best-supported values, mark them "not confirmed" in README and session handoff, and say so in the final message.
- Log: `log_check.py $WORK 2 metadata_approval pass|manual "<what was approved>"`.

### Phase 3 – Transcription (gate: build_score without errors)
Write `$WORK/score.json` bar by bar following `references/score-spec.md`; read `references/transcription-guide.md` first. If a MusicXML draft exists (from the user or an OMR tool), convert it with `musicxml_to_spec.py` and treat it as a draft only.
`python3 $S/build_score.py $WORK/score.json $WORK/score.musicxml --workdir $WORK` – fix every reported error (bar lengths, syllables hitting no note, ties).

### Phase 4 – Proofreading, twice (gate: both passes clean, findings resolved)
1. `python3 $S/check_music.py $WORK/score.json --workdir $WORK` – every finding (range, leap, rhythm) must be checked against the source; correct it or record it as `as_in_source`.
2. Render a proof: `python3 $S/render_score.py $WORK/score.musicxml $WORK/proof.pdf --lang <l> --spec $WORK/score.json --preview-dir $WORK/proof`.
3. **Pass 1 – pitches and rhythm:** for every system of the source compare the crops with your rendering bar by bar, voice by voice (note heads against staff lines, durations, ties vs slurs, accidentals). **Pass 2 – lyrics:** every verse, every syllable position, hyphens, extenders, voice-specific lines, punctuation, spelling as in the source.
3a. **Pass 3 – signs and lyric order:** run `python3 $S/signs_report.py $WORK/score.musicxml` and tick off every listed sign (dynamics, hairpins, repeats, endings, texts, fermatas) against the source crops, voice by voice; every `CHECK:` line must be resolved. For lyrics also write, for each bar of each system, the syllable sequence you read in the source ("bar, note no., syllable") and write it as `$WORK/source_read.json` (format in the script header) and run `python3 $S/check_lyrics_order.py $WORK/score.musicxml $WORK/source_read.json --part <voice number>`; every `DIFF` line is a finding to resolve (voices that share the text need one voice only). Log: `log_check.py $WORK 3 proof_signs pass "…"`.
4. If subagents are available, give pass 2 (or a full independent pass) to a fresh subagent that only gets the source crops and the proof previews and must list discrepancies – then reconcile. Otherwise, do the second pass after a deliberate break in a different order (last system first).
5. Every change → rebuild (Phase 3 command) and add an entry to docs.json `corrections` (kind, bar, voice, source, result, reason, status).
6. **Stop C (only if needed):** spots that proofreading could not settle from the source are asked together now (see the question plan), before score and audio are made. Without such spots there is no stop.
7. Log: `log_check.py $WORK 3 proof_pitch_rhythm pass "<n bars, n fixes>"` and `… 3 proof_lyrics pass "…"`.

### Phase 5 – Engraving (gate: readable, filled, looked at)
1. `python3 $S/render_score.py $WORK/score.musicxml "$PKG/<scores>/<Title>_<Score>.pdf" --lang <l> --spec $WORK/score.json --preview-dir $WORK/prev --write-xml $WORK/final.musicxml --workdir $WORK`
2. **Look at every preview page.** Check: everything on the 20 mm text axis, the cover page, the header line on every music page (title bold, Text, Musik), the header line with the page number right, the footer (date, EU AI label, AI note), no colliding syllables, hyphens visible and thin, enough space between the verse lines, dynamics not on top of notes. If something is off: try `--force pages=N,spp=M` or more pages; never go below the minimum scale.
3. `python3 $S/make_scores.py $WORK/final.musicxml "$PKG/<scores>" --slug <Title> --lang <l> --workdir $WORK` (choir + piano MusicXML).

### Phase 6 – Audio (gate: all files, spot check)
1. Trial: `python3 $S/make_audio.py $WORK/final.musicxml $WORK/score.json $WORK/trial --slug <Title> --only accomp:<voice>` – check duration and that the file starts with the own starting note and the pause, then the music (ffmpeg volumedetect on the first seconds).
2. Full: `python3 $S/make_audio.py $WORK/final.musicxml $WORK/score.json "$PKG" --slug <Title> --workdir $WORK` (takes several minutes; may run in the background only while no question to the user is open).
3. Spot check one stage-3 file: own voice vs. a neighbour stem level difference ≈ 7 dB (measure, don't assume).
4. **Technical listening test:** `python3 $S/audio_check.py "$PKG" $WORK/score.json --workdir $WORK` compares every MP3 with its MIDI (duration, silence where notes should sound, clipping, loudness, both ears filled, solo centred; about 1.5 minutes). Pass → say nothing, the log row is enough. Problems → fix the cause, rerun `make_audio.py` and the test (max 3 rounds). What is still wrong after round 3 goes into the final message (see there). It does not judge sound or musicality and does not measure the stage-3 level mix; that stays with the user's ears and the spot check above.

### Phase 7 – Documentation and package (gate: verify passes, ZIPs tested)
1. `python3 $S/make_overview.py "$PKG/mixes.json" $WORK/score.json "$PKG/<practice>/<Title>_<Overview>.pdf" --png $WORK/overview.png --workdir $WORK` – look at the PNG.
2. Write `$WORK/docs.json` (source file name, meta sources with URLs and approval, notes and open points in the user language **and** English, all corrections).
3. Write `$PKG/session_handoff.md` from `assets/templates/session_handoff.<lang>.md` (in the user language; decisions, data, corrections, open points of this piece). **Never type facts that the build knows**: use the tokens in double curly braces `date`, `package`, `skill_version`, `folders`, `score_layout`, `project_data` (as in the template); `make_layout.py` fills them and fails if the handoff lacks the package name, version, date or a top-level folder.
4. `python3 $S/make_docs.py $WORK/score.json $WORK/docs.json "$PKG" --workdir $WORK --mixes "$PKG/mixes.json" --layout "<score pdf>.layout.json"`
5. `python3 $S/verify.py "$PKG" $WORK/score.json --workdir $WORK` – fix failures (max 3 rounds), then run make_docs again so the check log contains the verify result. verify.py also compares every MIDI file with the final MusicXML (tempo, starting notes, onset and pitch of every note per voice, lost notes). That finds errors of the audio step, not transcription errors – the MIDI comes from the same MusicXML, so Phase 4 against the source stays the only check against the original. If the check is skipped (mido missing), say so in the final message.
6. `python3 $S/package.py "$PKG" $WORK/score.json --source source.pdf --workdir $WORK --docs $WORK/docs.json --out <output dir>`
   package.py leaves the work package untouched and builds the delivery folder next to it (see Deliverables). If anything is changed afterwards, rerun make_docs (`--mixes "$PKG/mixes.json" --layout "$PKG/<scores>/<Title>_<Score>.layout.json"`), then verify and package again – never ship ZIPs built before the last docs change. 
   package.py runs `make_layout.py`: delivery layout, score copy per voice, MP3 tags, self-check (numbering without gaps, max 3 folder levels, no identical files stored twice, tags present, guides one page, files per voice folder, and the consistency rules below), then builds **one** ZIP `<date>_Chor_Uebungen_<Title>.zip` that contains the numbered folders directly (no extra top folder). Re-running package.py replaces earlier ZIPs of the same title. package.py builds the delivery folder twice: the second pass has the check log regenerated with this run's delivery check (the ZIP check itself cannot be inside the ZIP and is left out of the log).
7. `python3 $S/run_stats.py $WORK --zip <delivery ZIP>` – prints and saves the run statistics (longest log gaps, audio generation time, waiting time, scope, check rounds, corrections, ZIP size by file type). Use it in the final message in two or three lines; it cannot know tokens.
8. Look at one voice folder guide, one score page and the director guide (pdftoppm), then deliver the **one** ZIP (file-sending tool; never send a second ZIP) and the final message.

### Phase 8 – Closing: improvement proposals only if they pass a sensibility test
Goal: improve the skill without costing tokens or overwhelming the user. **Default is to do nothing and say nothing.** The piece handoff (Phase 7) is always written; everything below only happens when the check in step 1 finds something.
1. Collect candidates (no tool calls, no file reading): wrong assumptions of the skill, missed checks, tool failures, user corrections caused by the skill, steps that needed several rounds, and what you could not judge alone (scan quality, piece-specific features, matters of taste, untested ideas) – a later score may share them.
   **Sensibility test – a candidate is proposed only if all of these hold, otherwise drop it silently:** (a) it would apply to other scores, not only this piece; (b) it can be fixed concretely in one place of the skill; (c) the benefit is clearly larger than the complexity it adds – the skill must not grow heavier, longer or harder to use for rare cases; (d) it is not already covered and does not contradict an existing rule; (e) it is small enough to be tested in one run. A candidate that fails only (a) may be offered as "only this piece" (goes into the piece handoff, not into the skill).
2. **Nothing passes the test → stop here.** Add nothing to the final message except, at most, one short line ("keine Skill-Verbesserungen aus dieser Sitzung"). No question, no skill handoff, no new version. There is no fixed number of proposals: it is as many as pass the test, usually zero to two; if more than four pass, propose only the four with the best benefit-to-complexity ratio and say that others were dropped.
3. Proposals → in the final message one short list (one line each: what happened, proposed change, what it adds to the skill) and **one** `AskUserQuestion` (multi-select, one option per proposal, "none" included, free text). Do not apply anything unasked.
4. Only after the user chose: apply the change in a working copy, write a short skill handoff from `assets/templates/skill_handoff.en.md` (file name `session-handoff.md` in the skill folder; changes, why, open points – English, no piece-specific content), run `python3 $S/check_third_party.py` and fill section 5 "Third-party rights check" of the skill handoff (mandatory, `release.py` stops when the check fails), then run `python3 $S/release.py <skill dir copy> --out <dir> --bump patch|minor --note "<one line per change>"` (updates `VERSION`, `CHANGELOG.md` and the version in both READMEs, builds `<out>/choir-practice.skill` (constant file name so that uploading replaces the skill) and `<out>/RELEASE_NOTES.md`) and deliver the `.skill`, `CHANGELOG.md` and `session-handoff.md`. Say plainly that the skill in the account is not changed automatically and the user saves the file locally; releases of the project itself run through GitHub (commit, tag `vX.Y.Z`, push; see README section 11). Never claim the account skill was updated.

## Error handling

| Situation | Response |
|---|---|
| Tool missing after setup | Use the fallback (FluidR3 soundfont), log it, tell the user what is missing in the result |
| Tested versions cannot be installed | Say so, offer the newest versions (ask), log them as not tested |
| Page unreadable (blur, cut off, too small) | Ask for a better scan of that page; ask with `AskUserQuestion` (better scan / continue without that page) and wait; never invent the missing part |
| Single spot unreadable | Most likely reading + `uncertain` correction entry + README open point |
| Source contradicts itself (e.g. verse text count ≠ notes) | Follow the musical logic, record it as `interpretation`, mention it to the user |
| Metadata not findable | Use what the source shows, mark "not confirmed", list as open point |
| Gate fails 3 times | Stop, show the user the failing check, the cause and options |
| Language without pack | Create the pack (see Language), get the user's OK on names |
| Unsupported notation (e.g. aleatoric passages, cluster) | Notate the closest standard form, `interpretation` entry, tell the user |

## Final message to the user (in their language)

Lead with the result: what was delivered (one ZIP with the folders 1_Noten … 4_Werkzeuge; the voice ZIPs in 2_Ueben can be passed on as they are), score pages and readability, number of audio files. Then in short lines: approved vs. not confirmed work details (with links), number of corrections and uncertain spots (point to the correction log), what was not checked (the audio is tested technically; sound quality is not judged), one natural next step. **Audio test:** mention it only if `audio_check.py` still reported problems after the repeat rounds (one short line per file, with the problem); a clean test is not mentioned. No recap of the steps. Skill improvement proposals (Phase 8) appear only if they passed the sensibility test, as a short list with one question.

## Reference files
- `references/score-spec.md` – score.json and docs.json formats (read before Phase 3)
- `references/transcription-guide.md` – reading scans reliably, proofreading protocol, what goes into the correction log
- `references/musical-defaults.md` – tempo terms, voice ranges, seating, melody, levels and why
- `assets/templates/session_handoff.<lang>.md` – session handoff structure (per piece, one per language; `check_templates.py` keeps all languages in step)
- `assets/templates/skill_handoff.en.md` – handoff for changes to the skill itself
- `assets/i18n/*.json` – language packs
