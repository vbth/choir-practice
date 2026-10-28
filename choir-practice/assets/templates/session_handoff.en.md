# Session handoff: <Title> – choir practice package

**Date:** {{date}} · **Created with:** choir-practice skill {{skill_version}} · **User language:** <lang>

## 0. Instructions for the next chat
You are continuing work on a finished choir practice package. **First run `bash <skill dir>/scripts/setup.sh` and wait for every tool ok** (fresh environments have no audio/notation tools). Then read this file completely. Use the values in section 4 exactly. Do not reopen decisions in section 3 unless the user asks. Reply first with at most 5 lines: piece, state, open points (section 6), next step – then wait for the user.

## 1. Piece
- Title / subtitle:
- Composer / arranger / lyricist (+ approval status and source URLs):
- Voicing, voices and clefs:
- Key, time signature (changes), pickup, number of bars, verses/refrain structure:

## 2. Source
- Supplied file, type (scan / export), quality, page count:
- Special features (voice-specific lyric lines, dotted arcs, repeats, accompaniment):

## 3. Decisions
| Decision | Reason / approved by |
|---|---|
| Melody voice | |
| Seating (left → right) | |
| Tempo (marking, bpm, beat) | |
| Score layout | {{score_layout}} |
| Rights (status, intended use, reference) | |

## 4. Exact data
- Package: {{package}} (date {{date}}); top-level folders: {{folders}}
- Number of files, voice folders:
- Audio settings: stages and levels, soundfont, loudness, slow tempo %:

## 5. Corrections and checks
- Number of correction-log entries by status (corrected / as in source / interpretation / uncertain) and the important ones:
- Gates passed (setup, survey, metadata, transcription, proof ×2, engraving, audio, verify, package):

## 6. Open points
- <uncertain spots, unconfirmed metadata, things not checked (audio tested technically only, sound not judged)>

<!-- Facts the build knows are written as tokens in double curly braces (date, package, skill_version, folders, score_layout, project_data); make_layout.py fills them. Never type them by hand. -->

## 7. How to change something
Edit `{{project_data}}/score.json` (project data folder of the package) (format: references/score-spec.md), then rerun from build_score.py (Phase 3) through package.py (Phase 7) with the same language and date rules; add a correction-log entry for every change.
