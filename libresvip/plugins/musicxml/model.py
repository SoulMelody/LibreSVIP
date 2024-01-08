from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from libresvip.model.base import Note, SongTempo, TimeSignature


@dataclass
class KeyTick:
    tick: int
    tempo: Optional[SongTempo] = None
    note_start: Optional[Note] = None
    note_end: Optional[Note] = None
    track_index: Optional[int] = None


@dataclass
class MXmlMeasureContent:
    class NoteType(enum.IntEnum):
        BEGIN = 1
        MIDDLE = 2
        END = 3
        SINGLE = 4

    duration: int
    note: Optional[Note]
    note_type: Optional[NoteType]
    bpm: Optional[float] = None

    @classmethod
    def with_tempo(cls, bpm: float) -> MXmlMeasureContent:
        return cls(duration=0, note=None, note_type=None, bpm=bpm)

    @classmethod
    def with_rest(cls, duration: int) -> MXmlMeasureContent:
        return cls(duration=duration, note=None, note_type=None, bpm=None)

    @classmethod
    def with_note(cls, duration: int, note: Note, note_type: NoteType) -> MXmlMeasureContent:
        return cls(duration=duration, note=note, note_type=note_type, bpm=None)


@dataclass
class MXmlMeasure:
    tick_start: int
    length: int
    time_signature: Optional[TimeSignature] = None
    contents: Optional[list[MXmlMeasureContent]] = None
