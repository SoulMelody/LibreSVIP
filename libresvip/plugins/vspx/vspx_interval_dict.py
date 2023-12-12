import functools
import math

import more_itertools
import portion

from libresvip.core.time_interval import PiecewiseIntervalDict
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.point import (
    Point,
)

from .model import VocalSharpNoteTrack


def vspx_cosine_easing_in_out_interpolation(
    x: int, start: tuple[float, float], end: tuple[float, float]
) -> float:
    x0, y0 = start
    x1, y1 = end
    return (y0 + y1) / 2 + (y0 - y1) * math.cos((x - x0) / (x1 - x0) * math.pi) / 2


def vspx_key_interval_dict(
    note_track: VocalSharpNoteTrack,
    synchronizer: TimeSynchronizer,
) -> PiecewiseIntervalDict:
    interval_dict = PiecewiseIntervalDict()
    for is_first, is_last, (prev_note, next_note) in more_itertools.mark_ends(
        more_itertools.pairwise(note_track.note)
    ):
        if is_first:
            interval_dict[portion.closedopen(0, prev_note.pos)] = prev_note.key_number
        middle_pos = (prev_note.end_pos + next_note.pos) // 2
        interval_dict[
            portion.closedopen(prev_note.pos, middle_pos)
        ] = prev_note.key_number
        interval_dict[
            portion.closedopen(
                middle_pos,
                next_note.end_pos,
            )
        ] = next_note.key_number
        if is_last:
            interval_dict[
                portion.closedopen(next_note.pos, portion.inf)
            ] = next_note.key_number
        if note_track.por > 0:
            por_start = synchronizer.get_actual_ticks_from_secs_offset(
                middle_pos, -note_track.por
            )
            por_end = synchronizer.get_actual_ticks_from_secs_offset(
                middle_pos, note_track.por
            )
            interval_dict[portion.closedopen(por_start, por_end)] = functools.partial(
                vspx_cosine_easing_in_out_interpolation,
                start=Point(x=por_start, y=prev_note.key_number),
                end=Point(x=por_end, y=next_note.key_number),
            )
    return interval_dict
