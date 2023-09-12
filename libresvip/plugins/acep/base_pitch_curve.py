import dataclasses
import math
from typing import Iterable

from pydantic import Field

from .model import AcepNote, AcepTempo
from .time_utils import tick_to_second


@dataclasses.dataclass
class NoteInSeconds:
    semitone: int
    start: float = 0.0
    end: float = 0.0


def _convolve(note_list: list[NoteInSeconds]) -> list[float]:
    total_points = round(1000 * (note_list[-1].end + 0.12)) + 1
    init_values = [0.0] * total_points
    note_index = 0
    for i in range(total_points):
        init_values[i] = note_list[note_index].semitone
        if note_index < len(note_list) - 1:
            ts = 0.001 * i
            if ts >= 0.5 * (
                note_list[note_index].end + note_list[note_index + 1].start
            ):
                note_index += 1
    kernel = [0.0] * 119
    for i in range(119):
        ts = 0.001 * (i - 59)
        kernel[i] = math.cos(math.pi * ts / 0.12)
    kernel_sum = sum(kernel)
    for i in range(119):
        kernel[i] /= kernel_sum
    convolve_values = [0.0] * total_points
    for i in range(total_points):
        for j in range(119):
            clipped_index = min(max(i - 59 + j, 0), total_points - 1)
            convolve_values[i] += kernel[j] * init_values[clipped_index]
    return convolve_values


@dataclasses.dataclass
class BasePitchCurve:
    notes: dataclasses.InitVar[Iterable[AcepNote]]
    tempos: dataclasses.InitVar[list[AcepTempo]]
    tick_offset: dataclasses.InitVar[int] = 0
    values_in_semitone: list[float] = Field(default_factory=list)

    def __post_init__(
        self, notes: Iterable[AcepNote], tempos: list[AcepTempo], tick_offset: int = 0
    ):
        notes = list(notes)
        skipped_tempos = [
            AcepTempo(
                position=tempo.position - tick_offset,
                bpm=tempo.bpm,
            )
            for tempo in tempos
            if tempo.position >= tick_offset
        ]
        if not (len(skipped_tempos) > 0 >= skipped_tempos[0].position):
            i = 0
            while i < len(tempos) and tempos[i].position <= tick_offset:
                i += 1
            skipped_tempos.insert(0, AcepTempo(position=0, bpm=tempos[i - 1].bpm))
        note_list = [
            NoteInSeconds(
                start=tick_to_second(note.pos, skipped_tempos),
                end=tick_to_second(note.pos + note.dur, skipped_tempos),
                semitone=note.pitch,
            )
            for note in notes
        ]
        self.values_in_semitone = _convolve(note_list)

    def semitone_value_at(self, seconds: float) -> float:
        position = 1000 * max(0.0, seconds)
        left_index = math.floor(position)
        lambda_ = position - left_index
        clipped_left_index = min(int(left_index), len(self.values_in_semitone) - 1)
        clipped_right_index = min(
            clipped_left_index + 1, len(self.values_in_semitone) - 1
        )
        return (1 - lambda_) * self.values_in_semitone[
            clipped_left_index
        ] + lambda_ * self.values_in_semitone[clipped_right_index]
