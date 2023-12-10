import functools

import more_itertools
import portion

from libresvip.core.time_interval import PiecewiseIntervalDict
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import Note
from libresvip.model.point import Point, cosine_easing_in_out_interpolation


def vspx_key_interval_dict(
    notes: list[Note],
    por: float,
    synchronizer: TimeSynchronizer,
) -> PiecewiseIntervalDict:
    interval_dict = PiecewiseIntervalDict()
    for is_first, is_last, (prev_note, next_note) in more_itertools.mark_ends(
        more_itertools.pairwise(notes)
    ):
        if is_first:
            interval_dict[
                portion.closedopen(0, prev_note.start_pos)
            ] = prev_note.key_number
        middle_pos = (prev_note.end_pos + next_note.start_pos) // 2
        interval_dict[
            portion.closedopen(prev_note.start_pos, middle_pos)
        ] = prev_note.key_number
        interval_dict[
            portion.closedopen(
                middle_pos,
                next_note.end_pos,
            )
        ] = next_note.key_number
        if is_last:
            interval_dict[
                portion.closedopen(next_note.start_pos, portion.inf)
            ] = next_note.key_number
        if por > 0:
            por_start = synchronizer.get_actual_ticks_from_secs_offset(middle_pos, -por)
            por_end = synchronizer.get_actual_ticks_from_secs_offset(middle_pos, por)
            interval_dict[portion.closedopen(por_start, por_end)] = functools.partial(
                cosine_easing_in_out_interpolation,
                start=Point(x=por_start, y=prev_note.key_number),
                end=Point(x=por_end, y=next_note.key_number),
            )
    return interval_dict
