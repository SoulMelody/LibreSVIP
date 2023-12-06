import dataclasses
import math
from typing import Iterable

from more_itertools import convolve

from .model import AcepNote, AcepTempo
from .time_utils import tick_to_second


@dataclasses.dataclass
class NoteInSeconds:
    semitone: int
    start: float = 0.0
    end: float = 0.0


@dataclasses.dataclass
class NoteVibrato:
    start: float
    end: float
    amplitude: float
    frequency: float
    phase: float
    attack_time: float
    release_time: float
    attack_level: float
    release_level: float


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
    return list(convolve(init_values, kernel))[59:-59]


@dataclasses.dataclass
class BasePitchCurve:
    notes: dataclasses.InitVar[Iterable[AcepNote]]
    tempos: dataclasses.InitVar[list[AcepTempo]]
    tick_offset: dataclasses.InitVar[int] = 0
    vibrato_list: list[NoteVibrato] = dataclasses.field(default_factory=list)
    values_in_semitone: list[float] = dataclasses.field(default_factory=list)

    def __post_init__(
        self, notes: Iterable[AcepNote], tempos: list[AcepTempo], tick_offset: int
    ):
        note_list = []
        for note in notes:
            note_end = tick_to_second(note.pos + note.dur + tick_offset, tempos)
            note_list.append(
                NoteInSeconds(
                    start=tick_to_second(note.pos + tick_offset, tempos),
                    end=note_end,
                    semitone=note.pitch,
                )
            )
            if note.vibrato is not None:
                vibrato_start = tick_to_second(
                    note.pos + note.vibrato.start_pos + tick_offset, tempos
                )
                vibrato_duration = note_end - vibrato_start
                self.vibrato_list.append(
                    NoteVibrato(
                        start=vibrato_start,
                        end=note_end,
                        amplitude=note.vibrato.amplitude,
                        frequency=note.vibrato.frequency,
                        phase=note.vibrato.phase,
                        attack_time=vibrato_start
                        + note.vibrato.attack_ratio * vibrato_duration,
                        release_time=note_end
                        - note.vibrato.release_ratio * vibrato_duration,
                        attack_level=note.vibrato.attack_level,
                        release_level=note.vibrato.release_level,
                    )
                )
        self.values_in_semitone = _convolve(note_list)

    def semitone_value_at(self, seconds: float) -> float:
        position = 1000 * max(0.0, seconds)
        left_index = math.floor(position)
        lambda_ = position - left_index
        clipped_left_index = min(int(left_index), len(self.values_in_semitone) - 1)
        clipped_right_index = min(
            clipped_left_index + 1, len(self.values_in_semitone) - 1
        )
        pitch_value = (1 - lambda_) * self.values_in_semitone[
            clipped_left_index
        ] + lambda_ * self.values_in_semitone[clipped_right_index]
        if (
            vibrato := next(
                (
                    vibrato
                    for vibrato in self.vibrato_list
                    if vibrato.start <= seconds < vibrato.end
                ),
                None,
            )
        ) is not None:
            vibrato_value = (
                math.sin(
                    math.pi
                    * (
                        2 * (seconds - vibrato.start) * vibrato.frequency
                        + vibrato.phase
                    )
                )
                * vibrato.amplitude
                * 0.5
            )
            if seconds < vibrato.attack_time:
                vibrato_value *= (
                    vibrato.attack_level
                    * (seconds - vibrato.start)
                    / (vibrato.attack_time - vibrato.start)
                )
            elif seconds >= vibrato.release_time:
                vibrato_value *= (
                    vibrato.release_level
                    * (vibrato.end - seconds)
                    / (vibrato.end - vibrato.release_time)
                )
            else:
                ratio = (seconds - vibrato.attack_time) / (
                    vibrato.release_time - vibrato.attack_time
                )
                vibrato_value *= vibrato.attack_level + ratio * (
                    vibrato.release_level - vibrato.attack_level
                )
            pitch_value += vibrato_value
        return pitch_value
