import dataclasses
import functools
import math
from typing import Optional, Union

import more_itertools
import portion

from libresvip.core.time_interval import PiecewiseIntervalDict
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.utils.music_math import cosine_easing_in_out_interpolation

from .model import VocalSharpDefaultTrill, VocalSharpNoteTrack, VocalSharpTrill


def vspx_sine_vibrato_interpolation(
    seconds: float,
    vibrato_start: float,
    trill: Union[VocalSharpTrill, VocalSharpDefaultTrill],
) -> float:
    return (
        math.sin(math.pi * (2 * (seconds - vibrato_start) * trill.frequency + trill.phase))
        * trill.amplitude
    )


def vspx_cosine_vibrato_coef_attack_interpolation(
    seconds: float, vibrato_start: float, por: float
) -> float:
    return 1 - math.cos(math.pi * (0.5 * (seconds - vibrato_start) / por))


def vspx_cosine_vibrato_coef_release_interpolation(
    seconds: float, vibrato_end: float, por: float
) -> float:
    return 1 - math.cos(math.pi * (0.5 * (vibrato_end - seconds) / por))


@dataclasses.dataclass
class BasePitchCurve:
    note_track: dataclasses.InitVar[VocalSharpNoteTrack]
    default_trill: dataclasses.InitVar[Optional[VocalSharpDefaultTrill]]
    synchronizer: TimeSynchronizer
    key_interval_dict: PiecewiseIntervalDict = dataclasses.field(
        default_factory=PiecewiseIntervalDict
    )
    vibrato_value_interval_dict: PiecewiseIntervalDict = dataclasses.field(
        default_factory=PiecewiseIntervalDict
    )
    vibrato_coef_interval_dict: PiecewiseIntervalDict = dataclasses.field(
        default_factory=PiecewiseIntervalDict
    )

    def __post_init__(
        self,
        note_track: VocalSharpNoteTrack,
        default_trill: Optional[VocalSharpDefaultTrill] = None,
    ) -> None:
        if not len(note_track.note):
            pass
        elif len(note_track.note) == 1:
            note = note_track.note[0]
            self.key_interval_dict[portion.closedopen(0, portion.inf)] = note.key_number
            if (trill := note.trill or default_trill) is not None:
                vibrato_start_secs = (
                    self.synchronizer.get_actual_secs_from_ticks(note.pos) + trill.pos
                )
                vibrato_end_secs = self.synchronizer.get_actual_secs_from_ticks(
                    note.pos + note.duration
                )
                if vibrato_end_secs > vibrato_start_secs:
                    self.set_vspx_vibrato_curve(
                        vibrato_start_secs,
                        vibrato_end_secs,
                        trill,
                        note_track.por,
                    )
        else:
            for is_first, is_last, (
                prev_note,
                next_note,
            ) in more_itertools.mark_ends(more_itertools.pairwise(note_track.note)):
                prev_start_secs = self.synchronizer.get_actual_secs_from_ticks(prev_note.pos)
                prev_end_secs = self.synchronizer.get_actual_secs_from_ticks(
                    prev_note.pos + prev_note.duration
                )
                next_start_secs = self.synchronizer.get_actual_secs_from_ticks(next_note.pos)
                next_end_secs = self.synchronizer.get_actual_secs_from_ticks(
                    next_note.pos + next_note.duration
                )
                if is_first:
                    self.key_interval_dict[portion.closedopen(0, prev_start_secs)] = (
                        prev_note.key_number
                    )
                middle_secs = (prev_end_secs + next_start_secs) / 2
                self.key_interval_dict[portion.closedopen(prev_start_secs, middle_secs)] = (
                    prev_note.key_number
                )
                self.key_interval_dict[
                    portion.closedopen(
                        middle_secs,
                        next_end_secs,
                    )
                ] = next_note.key_number
                if is_last:
                    self.key_interval_dict[portion.closedopen(next_start_secs, portion.inf)] = (
                        next_note.key_number
                    )
                    if (trill := next_note.trill or default_trill) is not None:
                        vibrato_start_secs = next_start_secs + trill.pos
                        vibrato_end_secs = next_end_secs
                        if vibrato_end_secs > vibrato_start_secs:
                            self.set_vspx_vibrato_curve(
                                vibrato_start_secs,
                                vibrato_end_secs,
                                trill,
                                note_track.por,
                            )
                if note_track.por > 0:
                    por_start = middle_secs - note_track.por
                    por_end = middle_secs + note_track.por
                    self.key_interval_dict[portion.closedopen(por_start, por_end)] = (
                        functools.partial(  # type: ignore[call-arg]
                            cosine_easing_in_out_interpolation,
                            start=(por_start, prev_note.key_number),
                            end=(por_end, next_note.key_number),
                        )
                    )
                if (trill := prev_note.trill or default_trill) is not None:
                    vibrato_start_secs = prev_start_secs + trill.pos
                    vibrato_end_secs = (prev_end_secs + next_start_secs) / 2
                    if vibrato_end_secs > vibrato_start_secs:
                        self.set_vspx_vibrato_curve(
                            vibrato_start_secs,
                            vibrato_end_secs,
                            trill,
                            note_track.por,
                        )

    def set_vspx_vibrato_curve(
        self,
        start: float,
        end: float,
        trill: Union[VocalSharpTrill, VocalSharpDefaultTrill],
        por: Optional[float] = None,
    ) -> None:
        self.vibrato_value_interval_dict[portion.closed(start, end)] = functools.partial(
            vspx_sine_vibrato_interpolation,
            vibrato_start=start,
            trill=trill,
        )
        if por is None or (end - start) < por * 2:
            middle = (start + end) / 2
            half = (end - start) / 2
            self.vibrato_coef_interval_dict[portion.closedopen(start, middle)] = functools.partial(
                vspx_cosine_vibrato_coef_attack_interpolation,
                vibrato_start=start,
                por=half,
            )
            self.vibrato_coef_interval_dict[portion.closed(middle, end)] = functools.partial(
                vspx_cosine_vibrato_coef_release_interpolation,
                vibrato_end=end,
                por=half,
            )
        elif por:
            self.vibrato_coef_interval_dict[portion.closedopen(start, start + por)] = (
                functools.partial(
                    vspx_cosine_vibrato_coef_attack_interpolation,
                    vibrato_start=start,
                    por=por,
                )
            )
            self.vibrato_coef_interval_dict[portion.closed(start + por, end - por)] = 1
            self.vibrato_coef_interval_dict[portion.openclosed(end - por, end)] = functools.partial(
                vspx_cosine_vibrato_coef_release_interpolation,
                vibrato_end=end,
                por=por,
            )
        else:
            self.vibrato_coef_interval_dict[portion.closed(start, end)] = 0

    def semitone_value_at(self, seconds: float) -> Optional[float]:
        if (pitch_value := self.key_interval_dict.get(seconds)) is not None and (
            vibrato_value := self.vibrato_value_interval_dict.get(seconds)
        ) is not None:
            vibrato_value *= self.vibrato_coef_interval_dict[seconds]
            pitch_value += vibrato_value
        return pitch_value
