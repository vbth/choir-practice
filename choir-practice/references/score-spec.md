# score.json and docs.json

## Contents
1. score.json – top level
2. Music tokens
3. Lyrics
4. Directions, barlines, changes
5. Complete example (invented SATB fragment)
6. docs.json

## 1. score.json – top level

| key | meaning |
|---|---|
| `language` | user language code, e.g. `"de"` – controls all names/texts |
| `meta` | `title`, optional `subtitle`, `composer`, `arranger`, `lyricist` (plain names, no "Text:" prefixes) |
| `tempo` | `text` (marking as printed), `bpm` (number), `beat` (`quarter`, `dotted-quarter`, `half`, `dotted-half`, `eighth`) |
| `key_fifths` | key signature (−7…7, flats negative) |
| `time` | `[beats, beat-type]` |
| `divisions` | ticks per quarter note; 4 covers 16ths and dotted 8ths, use 12 for triplets, 8 for 32nds |
| `pickup` | `true` if bar 0 is an incomplete pickup bar |
| `bar_number_offset` | first printed bar number of bar index 0 if the source does not start at 0/1 (default 0; a pickup is bar 0) |
| `voices` | list of `{"id", "name", "clef", "abbr"?, "voice_type"?}`; clef: `treble`, `treble8` (tenor), `bass`, `alto`, `tenor`; voice_type for range checks if the name is unusual |
| `seating` | voice IDs left → right as the choir stands (default: order of voices) |
| `melody` | ID of the voice carrying the melody (stage 2) |
| `rights` | `{"status": "public_domain"\|"licensed"\|"own"\|"unclear", "reference"?, "note"?, "notice"?, "permission"?: {"by", "date" (ISO)}, "licence"?: {"name", "url"}}` – asked at Stop A (`permission` only for `licensed`, `licence` only for `public_domain`); `notice` = © line printed in the source, unchanged; `unclear` with no `reference`, `note` or `notice` = no information: nothing about rights is written anywhere |
| `music` | `{voice id: [bar strings]}` – one string per bar, same number of bars for every voice |
| `lyrics` | see 3 |
| `directions` | see 4 |
| `barlines` | `{"bar index": "light-light"}` etc. (final bar gets light-heavy automatically) |
| `changes` | `{"bar index": {"time": [3,4], "key_fifths": 0}}` |

Bar index 0 is the pickup if `pickup` is true; otherwise bar 0 is the first full bar.

## 2. Music tokens

One token per note/rest, separated by spaces: `PITCH/DURATION[flags]`

- PITCH: step `A–G`, optional accidental `#`, `b`, `##`, `bb`, `n` (explicit natural), octave (C4 = middle C). Always write the **sounding** pitch spelled as in the source (tenor in treble-8 clef: written C5 = sounding `C4`).
- `r/DURATION` is a rest. DURATION in divisions (with divisions 4: 16th = 1, 8th = 2, dotted 8th = 3, quarter = 4, dotted quarter = 6, half = 8, dotted half = 12, whole = 16).
- Flags after the duration: `~` tie to the next note (same pitch), `(` `)` slur start/end, `{` `}` dotted slur start/end (dotted arcs in the source), `^` fermata.
- Accidentals are displayed automatically against key signature and earlier accidentals in the bar.
- Every bar must add up to the bar length (except pickup and final bar). Durations that are not a single note value must be split and tied.

## 3. Lyrics

```json
"lyrics": {
  "verses": {"1": "0:0:Sing | 1:0:a- | 1:2:loud | …", "2": "…"},
  "voice_overrides": {"B": {"bars": [7, 8], "verses": {"1": "7:0:… | 8:4:…"}}},
  "number_verses": true
}
```
- Token `bar:onset:syllable`; onset in divisions from the start of the bar.
- A syllable ending with `-` continues the word (hyphen); the next syllable ends it. Keep source hyphenation and spelling.
- Notes after a word-final syllable without own syllable get an extender line automatically (melisma, tied notes).
- The refrain printed once under verse 1 belongs to verse 1 only.
- `voice_overrides` replace the default tokens of the listed bars for one voice (e.g. a printed extra lyric line "2nd bass: …"). Use only where the source prints different text placement for that voice.
- Verse numbers ("1.", "2.") are added automatically when there is more than one verse.

## 4. Directions, barlines, changes

```json
"directions": [
  {"bar": 0, "onset": 0, "kind": "dyn", "value": "p"},
  {"bar": 6, "onset": 0, "kind": "wedge", "value": "crescendo"},
  {"bar": 6, "onset": "end", "kind": "wedge", "value": "stop"},
  {"bar": 9, "onset": 0, "kind": "words", "value": "rit.", "voices": ["S"]}
]
```
kind: `dyn` (pp…ff, sf…), `wedge` (`crescendo`, `diminuendo`, `stop`), `words` (italic text). `voices` limits a direction to some voices (default all). The tempo marking comes from `tempo.text` and is printed above the first staff.

## 5. Complete example (invented)

```json
{
 "language": "en",
 "meta": {"title": "Evening Song", "composer": "N. N.", "lyricist": "N. N."},
 "tempo": {"text": "Andante", "bpm": 72, "beat": "quarter"},
 "key_fifths": 1, "time": [4, 4], "divisions": 4, "pickup": false,
 "voices": [{"id": "S", "name": "Soprano", "clef": "treble"}, {"id": "A", "name": "Alto", "clef": "treble"},
            {"id": "T", "name": "Tenor", "clef": "treble8"}, {"id": "B", "name": "Bass", "clef": "bass"}],
 "seating": ["S", "A", "T", "B"], "melody": "S",
 "music": {
  "S": ["D5/4 B4/4 C5/4 D5/4", "E5/8~ E5/4 r/4"],
  "A": ["B4/4 G4/4 A4/4 B4/4", "C5/8~ C5/4 r/4"],
  "T": ["G3/4 D4/4 E4/4 D4/4", "G3/8~ G3/4 r/4"],
  "B": ["G2/4 G3/4( F#3/4) G3/4", "C3/8~ C3/4 r/4"]},
 "lyrics": {"verses": {"1": "0:0:Now | 0:4:the | 0:8:day | 0:12:is | 1:0:done."}},
 "directions": [{"bar": 0, "onset": 0, "kind": "dyn", "value": "mp"}]
}
```

## 6. docs.json

```json
{
 "source_file": "evening-song.pdf",
 "meta_sources": [{"field": "composer", "value": "N. N.", "url": "https://…", "approved": true}],
 "texts": {"de": {"notes": ["…"], "open": ["…"]}, "en": {"notes": ["…"], "open": ["…"]}},
 "corrections": [
  {"bar": 5, "voice": "A", "kind": "pitch", "source": "unclear note head (line/space)", "result": "F#4",
   "reason": {"de": "…", "en": "harmony and voice leading; check original"}, "status": "uncertain"}
 ]
}
```
- `texts` in the user language and English (README is bilingual). `notes`: what users should know about the source and the edition (e.g. dotted arcs rendered as dotted slurs). `open`: unresolved items.
- `corrections.source` / `result`: short, in the user language (the correction log is a user-facing file).
- `corrections.kind`: pitch, rhythm, lyrics, slur, dynamics, meta, layout, other. `status`: `corrected` (source error fixed – rare, always explain), `as_in_source` (flagged by a check but confirmed), `interpretation` (source ambiguous, reading chosen), `uncertain` (could not be confirmed – must also appear in `open`).


## 7. Repeats, endings and playback order
All measure numbers here are 1-based in MusicXML measure order (a pickup bar is measure 1).

**`repeats`** (optional, any number of repeat sections; engraved in the score **and** used for the audio). Each entry:
- `{"start": 2, "end": 7}` – repeat signs around measures 2–7, played twice. `"times": 4` plays it four times and prints `times="4"` on the closing sign.
- `{"start": 2, "endings": [[6,6],[7,7]]}` – with first and second ending brackets over measures 6 and 7. Pass 1 plays 2–5 and ending 1, pass 2 plays 2–5 and ending 2.
- Several passes under one bracket (verses on the same music): `{"start": 2, "endings": [{"passes": [1,2,3], "bars": [6,6]}, {"passes": [4], "bars": [7,7]}]}` prints "1,2,3" and "4"; the number of passes follows from the highest pass listed (or `"times"`). Any number of endings and passes works. A pass without an ending plays no ending.
- Several repeat sections in one piece: list them one after another (sorted by `start`, not overlapping). Nested repeats are not supported – write them out with `playback`.

**`performance_notes`** (optional): list of execution remarks that are printed in the source (for example "Verse 3: softer"), shown on the cover page of the score. Each entry is a string or `{"text": "…", "bar": 5}`; with `bar` (measure number) the cover adds "Bar 5, page 2" so the reader finds the place. The README should repeat them in its notes. They are text only; they do not change the audio.

**`playback`** (optional, audio only, wins over `repeats`): a list of `[first, last]` ranges in played order for **all MIDI and MP3 files**, for what signs cannot say – D.C./D.S./coda, a bridge, a verse that re-enters at another bar. Example: `[[1,7],[4,13]]` plays 1–7, then jumps back in at bar 4.

Notes:
- Without both keys the score is played once as printed.
- Dynamics, ties and starting notes follow the written-out order; starting notes come from the first sounding note of each voice.
- D.C./D.S./coda are not engraved as signs; add them as `directions` text if the source has them.
- Verses are sung from the score text; neither key changes lyrics.
- `verify.py` compares the MIDI with the same written-out order.
