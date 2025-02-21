from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from libresvip.model.base import Note, SongTempo, TimeSignature


@dataclass
class KeyTick:
    tick: int
    tempo: SongTempo | None = None
    note_start: Note | None = None
    note_end: Note | None = None
    track_index: int | None = None


@dataclass
class MXmlMeasureContent:
    class NoteType(enum.IntEnum):
        BEGIN = 1
        MIDDLE = 2
        END = 3
        SINGLE = 4

    duration: int
    note: Note | None
    note_type: NoteType | None
    bpm: float | None = None

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
    time_signature: TimeSignature | None = None
    contents: list[MXmlMeasureContent] | None = None
