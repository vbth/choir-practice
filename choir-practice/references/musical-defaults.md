# Musical defaults and their reasons

These defaults come from rehearsal practice; propose them, let the user approve (Phase 2), deviate when the piece demands it and say why.

## Practice stages (how a choir director rehearses a voice)
1. **Solo** – learn the line alone.
2. **With accompaniment** – own voice clearly on top, the melody (−4 dB) for context, a soft piano accompaniment of all voices (−12 dB) for harmony – like rehearsing at the piano with the director. Melody singers get own voice + accompaniment.
3. **In the choir** – hold the line against the others as in the real seating: neighbours left/right (−7 dB), edge voices get the next-but-one voice on the free side (−9 dB) so both ears are filled, the rest far out (−12 dB).
- **Tutti** – all voices equal, to hear the whole.
- **Slow (default 75 %, adjustable with `--slow-pct`)** for stages 1–2: difficult passages are learned slower.
- **Starting pitch**: voice files: only the own first note (the earliest note of that voice, even if it enters later); tutti: the first notes of all voices one after another, low to high, each 2.0 s long and 0.8 s apart; then a pause of 3.0 s (time to find the note), then straight into the music – a cappella choirs always get their note. Between the verses (every restart at measure 1) there is a pause of 2.0 s (`INTRO['verse_gap_s']`; at the slow tempo it scales with the tempo). No count-in clicks (they added nothing for singers; `COUNT_IN = True` in make_audio.py restores one bar).
- Levels −7/−9/−12 dB keep the other voices clearly audible without masking the own line; overall loudness −19 LUFS is comfortable on headphones.
- Two sounds for everything: choir sound (closer to singing, sustained) and optimised legato piano (clearer pitches). Detached piano notes sound choppy on repeated eighths – legato articulation is required.

## Tempo when the marking has no metronome number
| marking | beat = bpm |
|---|---|
| Largo, Grave, sehr langsam | 44–52 |
| Adagio, langsam | 56–66 |
| Andante, ruhig, gehend | 72–84 |
| Moderato, mäßig, fließend | 88–104 (compound metre: dotted quarter 56–66) |
| Allegretto, bewegt | 104–116 |
| Allegro, lebhaft, frisch | 120–140 |
| Presto, sehr schnell | 160+ |
In compound metres (6/8, 9/8, 12/8) give the tempo per dotted quarter. Present the choice for approval.

## Voice ranges (sounding, generous amateur limits used by check_music.py)
Soprano B3–C6 · Mezzo A3–A5 · Alto E3–F5 · Tenor A2–C5 · Baritone F2–G4 · Bass C2–F4. Notes outside are usually misreadings – but check the source before changing anything.

## Melody voice
Usually the highest voice (soprano; tenor 1 in male choir). Exceptions: arrangements with the tune in an inner voice (often marked, or recognisable as the well-known tune). Ask when unsure.

## Default seating (left → right, from the audience/conductor's view)
- SATB: S A T B (alternative S T B A for small choirs) · SSA(A): S1 S2 A (A1 A2) · TTBB: B2 B1 T2 T1 or T1 T2 B1 B2 · mixed with divisi: keep sections together, lower parts toward the middle.
Always confirm with the user – seating varies by choir and changes stage 3.

## Score layout
A4 portrait; staff space ≥ 1.6 mm; every voice its own staff; all verses under every staff, numbered; bar number at each system start matching the source; cover page first; header line on the music pages (title bold, text and music authors); footer left "date, EU label, AI note", right the page number, in lyric size; notation font Leland.
