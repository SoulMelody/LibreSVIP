import dataclasses
import functools
import math
from collections.abc import Iterable

import portion
from more_itertools import convolve

from libresvip.core.time_interval import PiecewiseIntervalDict
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.utils.music_math import linear_interpolation

from .model import AcepNote, AcepVibrato


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
            if ts >= 0.5 * (note_list[note_index].end + note_list[note_index + 1].start):
                note_index += 1
    kernel = [0.0] * 119
    for i in range(119):
        ts = 0.001 * (i - 59)
        kernel[i] = math.cos(math.pi * ts / 0.12)
    kernel_sum = sum(kernel)
    for i in range(119):
        kernel[i] /= kernel_sum
    return list(convolve(init_values, kernel))[59:-59]


def acep_vibrato_value_curve(seconds: float, vibrato_start: float, vibrato: AcepVibrato) -> float:
    return (
        math.sin(math.pi * (2 * (seconds - vibrato_start) * vibrato.frequency - vibrato.phase))
        * vibrato.amplitude
        * 0.5
    )


@dataclasses.dataclass
class BasePitchCurve:
    notes: dataclasses.InitVar[Iterable[AcepNote]]
    synchronizer: dataclasses.InitVar[TimeSynchronizer]
    tick_offset: dataclasses.InitVar[int] = 0
    vibrato_value_interval_dict: PiecewiseIntervalDict = dataclasses.field(
        default_factory=PiecewiseIntervalDict
    )
    vibrato_coef_interval_dict: PiecewiseIntervalDict = dataclasses.field(
        default_factory=PiecewiseIntervalDict
    )
    values_in_semitone: list[float] = dataclasses.field(default_factory=list)

    def __post_init__(
        self,
        notes: Iterable[AcepNote],
        synchronizer: TimeSynchronizer,
        tick_offset: int,
    ) -> None:
        note_list = []
        for note in notes:
            note_end = synchronizer.get_actual_secs_from_ticks(note.pos + note.dur + tick_offset)
            note_list.append(
                NoteInSeconds(
                    start=synchronizer.get_actual_secs_from_ticks(note.pos + tick_offset),
                    end=note_end,
                    semitone=note.pitch,
                )
            )
            if note.vibrato is not None:
                vibrato_start = synchronizer.get_actual_secs_from_ticks(
                    int(note.pos + note.vibrato.start_pos + tick_offset)
                )
                vibrato_duration = note_end - vibrato_start
                self.vibrato_value_interval_dict[portion.closed(vibrato_start, note_end)] = (
                    functools.partial(
                        acep_vibrato_value_curve,
                        vibrato_start=vibrato_start,
                        vibrato=note.vibrato,
                    )
                )
                attack_time = vibrato_start + note.vibrato.attack_ratio * vibrato_duration
                release_time = note_end - note.vibrato.release_ratio * vibrato_duration
                if note.vibrato.release_ratio:
                    self.vibrato_coef_interval_dict[portion.openclosed(release_time, note_end)] = (
                        functools.partial(
                            linear_interpolation,  # type: ignore[call-arg]
                            start=(release_time, note.vibrato.release_level),
                            end=(note_end, 0),
                        )
                    )
                self.vibrato_coef_interval_dict[portion.closed(attack_time, release_time)] = (
                    functools.partial(
                        linear_interpolation,  # type: ignore[call-arg]
                        start=(attack_time, note.vibrato.attack_level),
                        end=(release_time, note.vibrato.release_level),
                    )
                )
                if note.vibrato.attack_ratio:
                    self.vibrato_coef_interval_dict[
                        portion.closedopen(vibrato_start, attack_time)
                    ] = functools.partial(
                        linear_interpolation,  # type: ignore[call-arg]
                        start=(vibrato_start, 0),
                        end=(attack_time, note.vibrato.attack_level),
                    )
        self.values_in_semitone = _convolve(note_list)

    def semitone_value_at(self, seconds: float) -> float:
        position = 1000 * max(0.0, seconds)
        left_index = math.floor(position)
        lambda_ = position - left_index
        clipped_left_index = min(int(left_index), len(self.values_in_semitone) - 1)
        clipped_right_index = min(clipped_left_index + 1, len(self.values_in_semitone) - 1)
        pitch_value = (1 - lambda_) * self.values_in_semitone[
            clipped_left_index
        ] + lambda_ * self.values_in_semitone[clipped_right_index]
        if (vibrato_value := self.vibrato_value_interval_dict.get(seconds)) is not None:
            vibrato_value *= self.vibrato_coef_interval_dict[seconds]
            pitch_value += vibrato_value
        return pitch_value
