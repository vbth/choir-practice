#!/usr/bin/env python3
"""Strict schema of score.json (references/score-spec.md), the hand-over between musicxml_to_spec.py / the transcription and build_score.py.

  python3 score_schema.py score.json      validate one file (exit 1 with one line per problem)
  from score_schema import load_spec      json.load plus validation; exits with the problem list instead of a traceback

Unknown keys are errors (a typo such as "key_fifth" would otherwise be ignored silently). Bar lengths are not checked here: build_score.py does that."""
import json, re, sys
from typing import Annotated, Literal, Optional, Union
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator

TOK = re.compile(r'^(?:r|[A-G](?:##|bb|#|b|n)?-?\d)/\d+[~(){}^]*$')   # same grammar as build_score.TOK, pitch/duration[flags]
Pos = Annotated[int, Field(ge=0)]
Measure = Annotated[int, Field(ge=1)]   # 1-based, pickup = 1

class Strict(BaseModel):
    model_config = ConfigDict(extra='forbid')

class Meta(Strict):
    title: str; subtitle: Optional[str] = None; composer: Optional[str] = None; arranger: Optional[str] = None; lyricist: Optional[str] = None

class Tempo(Strict):
    text: Optional[str] = None
    bpm: Optional[Annotated[float, Field(gt=0, le=400)]] = None
    beat: Optional[Literal['quarter', 'dotted-quarter', 'half', 'dotted-half', 'eighth']] = 'quarter'   # null in a draft from musicxml_to_spec.py

class Voice(Strict):
    id: str = Field(min_length=1); name: str; abbr: Optional[str] = None
    clef: Literal['treble', 'treble8', 'bass', 'alto', 'tenor']
    voice_type: Optional[str] = None

class Rights(Strict):
    status: Literal['public_domain', 'licensed', 'own', 'unclear']
    use: Literal['rehearsal', 'commercial']
    reference: Optional[str] = None; note: Optional[str] = None; notice: Optional[str] = None

class VoiceOverride(Strict):
    bars: list[Pos]; verses: dict[str, str] = {}

class Lyrics(Strict):
    verses: dict[str, str] = {}; voice_overrides: dict[str, VoiceOverride] = {}; number_verses: bool = True

    @field_validator('verses')
    @classmethod
    def _verses(cls, v):
        for k, s in v.items(): check_lyric_tokens(f'verse {k}', s)
        return v

    @model_validator(mode='after')
    def _overrides(self):
        for vid, o in self.voice_overrides.items():
            for k, s in o.verses.items(): check_lyric_tokens(f'voice_overrides {vid} verse {k}', s)
        return self

def check_lyric_tokens(where, s):
    """Token `bar:onset:syllable`, separated by `|`."""
    for item in s.split('|'):
        item = item.strip()
        if item and not re.match(r'^\d+:\d+:\S.*$', item):
            raise ValueError(f'{where}: lyric token "{item}" is not bar:onset:syllable')

class Direction(Strict):
    bar: Pos; onset: Union[Pos, Literal['end']]; kind: Literal['dyn', 'wedge', 'words']; value: str
    voices: Optional[list[str]] = None

    @model_validator(mode='after')
    def _value(self):
        if self.kind == 'wedge' and self.value not in ('crescendo', 'diminuendo', 'stop'):
            raise ValueError(f'wedge value "{self.value}" must be crescendo, diminuendo or stop')
        if self.kind == 'dyn' and not re.match(r'^(?:[sfpz]+|[mfps]{1,3}|rfz?|sfz?p?)$', self.value):
            raise ValueError(f'dynamics value "{self.value}" is not a dynamics mark (p, mf, ff, sf, ...)')
        return self

class Change(Strict):
    time: Optional[Annotated[list[Annotated[int, Field(ge=1)]], Field(min_length=2, max_length=2)]] = None
    key_fifths: Optional[Annotated[int, Field(ge=-7, le=7)]] = None

class Ending(Strict):
    passes: Annotated[list[Annotated[int, Field(ge=1)]], Field(min_length=1)]
    bars: Annotated[list[Measure], Field(min_length=2, max_length=2)]

class Repeat(Strict):
    start: Measure; end: Optional[Measure] = None; times: Optional[Annotated[int, Field(ge=2)]] = None
    endings: Optional[list[Union[Ending, Annotated[list[Measure], Field(min_length=2, max_length=2)]]]] = None

    @model_validator(mode='after')
    def _shape(self):
        if (self.end is None) == (not self.endings): raise ValueError('a repeat needs exactly one of "end" or "endings"')
        if self.end is not None and self.end < self.start: raise ValueError(f'end {self.end} is before start {self.start}')
        return self

class Note(Strict):
    text: str; bar: Optional[Measure] = None

class Spec(Strict):
    language: str = Field(min_length=2, max_length=5)
    meta: Meta
    tempo: Tempo = Tempo()
    key_fifths: Annotated[int, Field(ge=-7, le=7)]
    time: Annotated[list[Annotated[int, Field(ge=1)]], Field(min_length=2, max_length=2)]
    divisions: Annotated[int, Field(ge=1, le=96)]
    pickup: bool = False
    bar_number_offset: int = 0
    voices: Annotated[list[Voice], Field(min_length=1)]
    seating: Optional[list[str]] = None
    melody: Optional[str] = None
    rights: Optional[Rights] = None
    music: dict[str, list[str]]
    lyrics: Lyrics = Lyrics()
    directions: list[Direction] = []
    barlines: dict[str, str] = {}
    changes: dict[str, Change] = {}
    repeats: Optional[list[Repeat]] = None
    playback: Optional[list[Annotated[list[Measure], Field(min_length=2, max_length=2)]]] = None
    performance_notes: Optional[list[Union[str, Note]]] = None

    @field_validator('time')
    @classmethod
    def _time(cls, v):
        if v[1] not in (1, 2, 4, 8, 16, 32): raise ValueError(f'beat-type {v[1]} is not a note value')
        return v

    @field_validator('music')
    @classmethod
    def _music(cls, v):
        for vid, bars in v.items():
            for bi, line in enumerate(bars):
                for tok in line.split():
                    if not TOK.match(tok): raise ValueError(f'{vid} bar {bi}: token "{tok}" is not PITCH/DURATION[flags], e.g. C5/4 or r/8~')
        return v

    @model_validator(mode='after')
    def _cross(self):
        ids = [v.id for v in self.voices]
        if len(set(ids)) != len(ids): raise ValueError(f'voice ids are not unique: {ids}')
        if set(self.music) != set(ids): raise ValueError(f'"music" has voices {sorted(self.music)}, "voices" lists {sorted(ids)}')
        counts = {k: len(b) for k, b in self.music.items()}
        if len(set(counts.values())) > 1: raise ValueError(f'voices have different numbers of bars: {counts}')
        nb = next(iter(counts.values()))
        if self.melody and self.melody not in ids: raise ValueError(f'melody "{self.melody}" is not a voice id')
        if self.seating and sorted(self.seating) != sorted(ids): raise ValueError(f'seating {self.seating} must list every voice id once: {ids}')
        for d in self.directions:
            if d.bar >= nb: raise ValueError(f'direction at bar {d.bar}: the piece has {nb} bars (0-based)')
            for x in d.voices or []:
                if x not in ids: raise ValueError(f'direction at bar {d.bar}: unknown voice "{x}"')
        for name, keys in (('barlines', self.barlines), ('changes', self.changes)):
            for k in keys:
                if not k.isdigit() or int(k) >= nb: raise ValueError(f'{name}: key "{k}" must be a bar index below {nb}')
        for vid in self.lyrics.voice_overrides:
            if vid not in ids: raise ValueError(f'lyrics.voice_overrides: unknown voice "{vid}"')
        for a, b in self.playback or []:
            if b < a or b > nb: raise ValueError(f'playback range [{a}, {b}] is outside measures 1..{nb}')
        for r in self.repeats or []:
            last = r.end if r.end is not None else max(e.bars[1] if isinstance(e, Ending) else e[1] for e in r.endings)
            if last > nb: raise ValueError(f'repeat starting at measure {r.start} ends at {last}, the piece has {nb} measures')
        return self

def format_errors(e, name='score.json'):
    out = []
    for x in e.errors():
        loc = '.'.join(str(p) for p in x['loc']) or '(top level)'
        out.append(f'{name}: {loc}: {x["msg"].removeprefix("Value error, ")}')
    return out

def validate_spec(data, name='score.json'):
    """Return the validated Spec; raise SystemExit with one line per problem."""
    try: return Spec.model_validate(data)
    except ValidationError as e:
        sys.exit(f'{len(e.errors())} problem(s) in the specification:\n  ' + '\n  '.join(format_errors(e, name)))

def load_spec(path):
    """json.load plus validation; returns the dict as in the file (extra defaults are not added)."""
    try: data = json.load(open(path, encoding='utf-8'))
    except json.JSONDecodeError as e: sys.exit(f'{path}: not valid JSON: {e}')
    validate_spec(data, path)
    return data

if __name__ == '__main__':
    if len(sys.argv) != 2: sys.exit('usage: score_schema.py score.json')
    load_spec(sys.argv[1]); print('score.json ok:', sys.argv[1])
