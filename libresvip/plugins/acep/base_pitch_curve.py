import dataclasses
import functools
import math
from collections.abc import Iterable
from itertools import islice

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


# Raised-cosine smoothing kernel: `cos(pi * t / 0.12)` sampled every millisecond
# over `t in [-0.059, 0.059]`, i.e. one tap per millisecond across a 119 tap
# window, then normalised to unit gain.
_KERNEL_SIZE = 119
_KERNEL_RADIUS = _KERNEL_SIZE // 2
_KERNEL_PERIOD = 0.12


def _sample_count(note_list: list[NoteInSeconds]) -> int:
    if not note_list:
        return 0
    return round(1000 * (note_list[-1].end + 0.12)) + 1


@functools.cache
def _kernel() -> tuple[float, ...]:
    # The multiplication order matches the reference formula exactly; `pi * a * b`
    # and `pi * (a * b)` round differently and would change the last digit.
    taps = []
    for index in range(_KERNEL_SIZE):
        ts = 0.001 * (index - _KERNEL_RADIUS)
        taps.append(math.cos(math.pi * ts / _KERNEL_PERIOD))
    gain = sum(taps)
    return tuple(tap / gain for tap in taps)


def _note_index_at(note_list: list[NoteInSeconds], sample_index: int) -> int:
    """Index of the note that is sounding at `sample_index` in the step signal.

    A note hands over to the next one once the sample time passes the midpoint
    between the two notes. Resolving that note by note instead of sample by
    sample is what lets the signal fill start anywhere: walking the samples from
    0 would advance at most one note per sample, but a note can only hand over
    after at least one sample per preceding handover, so both agree.
    """
    index = 0
    ts = 0.001 * sample_index
    while index < len(note_list) - 1 and ts >= 0.5 * (
        note_list[index].end + note_list[index + 1].start
    ):
        index += 1
    return index


def _step_signal(note_list: list[NoteInSeconds], start: int, stop: int) -> list[float]:
    """Samples `[start, stop)` of the per-millisecond semitone step function."""
    signal = [0.0] * (stop - start)
    note_index = _note_index_at(note_list, start)
    for offset in range(len(signal)):
        signal[offset] = note_list[note_index].semitone
        if note_index < len(note_list) - 1 and 0.001 * (start + offset) >= 0.5 * (
            note_list[note_index].end + note_list[note_index + 1].start
        ):
            note_index += 1
    return signal


def _convolve(note_list: list[NoteInSeconds], first_index: int = 0) -> list[float]:
    """Filtered semitone samples `first_index` through `_sample_count() - 1`.

    Convolution output `j` feeds sample `j - _KERNEL_RADIUS`, so nothing before
    sample `first_index` is ever queried and the earliest sample whose taps can
    still reach it is `first_index - _KERNEL_RADIUS`. Building the signal from
    there keeps every output bit-identical while making the cost follow the
    queried range instead of the song length.
    """
    total_points = _sample_count(note_list)
    if total_points == 0:
        return []
    first_index = min(first_index, total_points - 1)
    head = max(0, first_index - _KERNEL_RADIUS)
    return list(
        islice(
            convolve(_step_signal(note_list, head, total_points), _kernel()),
            _KERNEL_RADIUS + first_index - head,
            total_points + _KERNEL_RADIUS - head,
        )
    )


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
    first_query_secs: dataclasses.InitVar[float] = 0.0
    vibrato_value_interval_dict: PiecewiseIntervalDict = dataclasses.field(
        default_factory=PiecewiseIntervalDict
    )
    vibrato_coef_interval_dict: PiecewiseIntervalDict = dataclasses.field(
        default_factory=PiecewiseIntervalDict
    )
    values_in_semitone: list[float] = dataclasses.field(default_factory=list)
    values_offset: int = 0

    def __post_init__(
        self,
        notes: Iterable[AcepNote],
        synchronizer: TimeSynchronizer,
        tick_offset: int,
        first_query_secs: float,
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
        first_index = max(0, math.floor(1000 * max(0.0, first_query_secs)) - 60)
        total_points = _sample_count(note_list)
        first_index = min(first_index, total_points - 1) if total_points else 0
        self.values_offset = first_index
        self.values_in_semitone = _convolve(note_list, first_index)

    @property
    def values_length(self) -> int:
        return self.values_offset + len(self.values_in_semitone)

    def _value_at(self, index: int) -> float:
        if not self.values_in_semitone:
            return 0.0
        local_index = min(max(0, index - self.values_offset), len(self.values_in_semitone) - 1)
        return self.values_in_semitone[local_index]

    def semitone_value_at(self, seconds: float) -> float:
        position = 1000 * max(0.0, seconds)
        left_index = math.floor(position)
        lambda_ = position - left_index
        clipped_left_index = min(int(left_index), self.values_length - 1)
        clipped_right_index = min(clipped_left_index + 1, self.values_length - 1)
        pitch_value = (1 - lambda_) * self._value_at(clipped_left_index) + lambda_ * self._value_at(
            clipped_right_index
        )
        if (vibrato_value := self.vibrato_value_interval_dict.get(seconds)) is not None:
            vibrato_value *= self.vibrato_coef_interval_dict.get(seconds, 0)
            pitch_value += vibrato_value
        return pitch_value
