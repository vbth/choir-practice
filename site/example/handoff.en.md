# Session handoff: All My Ducklings – choir practice package

**Date:** {{date}} · **Created with:** choir-practice skill {{skill_version}} · **User language:** English

## 0. Instructions for the next chat
You are continuing work on a finished choir practice package. **First run `bash <skill dir>/scripts/setup.sh` and wait for every tool ok** (fresh environments have no audio/notation tools). Then read this file completely. Use the values in section 4 exactly as written. Do not reopen decisions from section 3 unless explicitly asked. Reply first with at most 5 lines: piece, status, open points (section 6), next step – then wait.

## 1. Piece
- Title: All My Ducklings (German original: Alle meine Entchen)
- Composer / lyricist: unknown (folk song), public domain (source: https://de.wikipedia.org/wiki/Alle_meine_Entchen, approved). The four-part setting is newly arranged (example package of the website). The English text is a machine translation of the German text (DeepL, provided by the user), with the last line shortened to fit the melody.
- Voices: soprano (treble clef), alto (treble clef), tenor (treble clef, one octave lower), bass (bass clef).
- C major, 2/4, no pickup, 20 bars, one verse, final fermata.

## 2. Source
- No source score: the notes are the starting point. The "Scan" file in the package is a copy of the engraved score.
- Special features: no voice-specific lyric lines, no repeats.

## 3. Decisions
| Decision | Reason / approved by |
|---|---|
| Melody voice | soprano |
| Seating (left → right) | S, A, T, B (assumption, not confirmed) |
| Tempo (marking, bpm, beat) | Cheerful, 150 per quarter; slow version 80 % |
| Score layout | {{score_layout}} |
| Rights (status, intended use, reference) | public domain, rehearsal, https://de.wikipedia.org/wiki/Alle_meine_Entchen |

## 4. Exact data
- Package: {{package}} (date {{date}}); top-level folders: {{folders}}
- Voice ZIP files: four (S, A, T, B), each with guide, score and all practice files in choir and piano sound.
- Audio settings: stages, levels, soundfont and loudness are in the check log; slow version 80 %.

## 5. Corrections and checks
- Correction log: no entries.
- Gates passed: see the check log.

## 6. Open points
- The audio files were not listened to, only checked technically; the sound is not judged.
- The seating S, A, T, B is an assumption.

<!-- Facts the build knows are written as tokens in double curly braces (date, package, skill_version, folders, score_layout, project_data); make_layout.py fills them. Never type them by hand. -->

## 7. How to change something
Edit `{{project_data}}/score.json` (project data folder of the package) (format: references/score-spec.md), then rerun from build_score.py (Phase 3) through package.py (Phase 7) with the same language and date rules; add a correction-log entry for every change.
