import dataclasses
from typing import Iterable

from pydantic import Field

from .model import AcepNote, AcepTempo
from .time_utils import tick_to_second


@dataclasses.dataclass
class NoteInSeconds:
    semitone: int
    start: float = 0.0
    end: float = 0.0


@dataclasses.dataclass
class BasePitchCurve:
    notes: dataclasses.InitVar[Iterable[AcepNote]]
    tempos: dataclasses.InitVar[list[AcepTempo]]
    tick_offset: dataclasses.InitVar[int] = 0
    note_list: list[NoteInSeconds] = Field(default_factory=list)
    values_in_semitone: list[float] = Field(default_factory=list)

    def __post_init__(
        self, notes: Iterable[AcepNote], tempos: list[AcepTempo], tick_offset: int = 0
    ):
        notes = list(notes)
        self.note_list = [
            NoteInSeconds(
                start=tick_to_second(note.pos, tempos),
                end=tick_to_second(note.pos + note.dur, tempos),
                semitone=note.pitch,
            )
            for note in notes
        ]

    def semitone_value_at(self, seconds: float) -> float:
        return next(
            (
                note.semitone
                for note in self.note_list
                if note.start <= seconds <= note.end
            ),
            0,
        )
