# Transcription guide – reading choral scores reliably

The single biggest risk of the whole package is a misread note or syllable. Scripts catch formal errors (bar lengths, syllables without notes); only careful visual comparison catches wrong pitches. Work slowly here; the steps after this run automatically.

## 1. Look at the source correctly
- Use `scan_tools.py crops` per system and segment (zoom 2.6–4). Dense chords: add `--guides` (lines/spaces labelled with sounding pitch names) and zoom further on single bars.
- Identify per staff: clef (treble with small 8 below = tenor, sounds an octave lower), key signature, time signature, which voices share the staff (stems up = upper voice, stems down = lower voice; one head with two stems = unison; two heads side by side = unison or second).
- Treble staff lines bottom→top: E4 G4 B4 D5 F5 (written); bass staff: G2 B2 D3 F3 A3. Spaces in between. For treble-8 subtract an octave for the sounding pitch.
- Photos can be tilted or distorted: read note heads relative to the nearest staff lines, not to absolute pixel rows.

## 2. Transcribe bar by bar
- Count the notes per bar per voice and check the sum against the time signature before writing pitches.
- Bars may break across systems (no barline at the end of a system) – check where barlines really are.
- Ties (solid arc, same pitch, one syllable) vs slurs (arc over different pitches or over repeated pitches with different syllables). Dotted arcs are editorial slurs: use `{ }`.
- Pickup bar = bar 0. Keep the source bar numbering; if the source starts with another number, set `bar_number_offset`.
- Repeats, voltas, D.C./D.S.: write the music as printed; set `repeats` (signs and endings) and, where needed, `playback` in score.json (references/score-spec.md) with the order the user confirmed, and say in docs.json notes how the audio is played. Without `playback` the audio plays the music once; verses are sung from the score.
- Several verses: each verse line aligns syllables under specific notes. Work column by column: for each note, which verse has a syllable here? A held syllable spans notes (melisma) – the extender/hyphen in the source shows it.
- Lines like "2nd bass: …" printed under a staff are voice-specific lyrics → `voice_overrides`.

## 3. Proofreading protocol (two passes)
**Pass 1 – pitches & rhythm.** For each system: source crop next to the rendered proof of the same bars. For each voice and bar: number of notes, each pitch (line/space), accidentals, durations/dots, ties/slurs, rests, fermatas, dynamics.
**Pass 2 – lyrics.** For each verse: every syllable under the right note, hyphens vs word ends, extenders, punctuation, capitalisation, spelling exactly as printed (old spellings stay), refrain only once, voice-specific lines.
Rules:
- Go through the source system by system; tick off bars explicitly; do not skim.
- Second pass in a different order (e.g. last system first) or by an independent subagent that sees only source crops and proof previews.
- Every `check_music.py` finding is resolved by looking at the source.
- Record the passes in the check log (bars compared, number of fixes).

## 4. Typical misreadings to look for
- Second-apart note heads in chords read as one note (or vice versa).
- Missing or extra 16ths in dotted rhythms; dotted 8th + 16th vs two 8ths.
- Time signature misread (6/8 vs 4/4 changes every bar length – check the first full bar).
- A voice silent in the pickup although a note is printed (shared stems).
- Ledger-line notes off by a third.
- Syllables dropped or merged ("Kirch-turm" read as one syllable), umlauts/ligatures lost, OCR letter swaps (c/e, rn/m, li/h).
- Title block cut off at the edge of a scan (→ research, Phase 2).

## 5. What goes into the correction log
Every place where the edition differs from a literal reading of the source or where you made a judgment: corrected engraving errors, interpretations of ambiguous marks (dotted arcs, unclear accidentals), unreadable spots (uncertain), findings confirmed as in the source, metadata completed from research. Each entry: bar, voice, kind, what the source shows, what the edition shows, reason, status.
