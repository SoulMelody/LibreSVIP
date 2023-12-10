import functools

import more_itertools
import portion

from libresvip.core.time_interval import PiecewiseIntervalDict
from libresvip.model.point import Point, cosine_easing_in_out_interpolation

from .model import PpsfDvlTrackEvent, PpsfNote


def ppsf_key_interval_dict(
    event_list: list[PpsfDvlTrackEvent], note_list: list[PpsfNote]
) -> PiecewiseIntervalDict:
    interval_dict = PiecewiseIntervalDict()
    if len(event_list) == 1:
        interval_dict[portion.closedopen(0, portion.inf)] = event_list[0].note_number
    else:
        for (
            is_first,
            is_last,
            ((prev_note, prev_event), (next_note, next_event)),
        ) in more_itertools.mark_ends(
            more_itertools.pairwise(zip(event_list, note_list))
        ):
            if is_first:
                interval_dict[
                    portion.closedopen(
                        0,
                        prev_note.pos
                        + prev_event.portamento_offset
                        + prev_event.portamento_length,
                    )
                ] = prev_note.note_number
            if next_event.portamento_length:
                interval_dict[
                    portion.closedopen(
                        prev_note.pos
                        + prev_event.portamento_offset
                        + prev_event.portamento_length,
                        next_note.pos + next_event.portamento_offset,
                    )
                ] = prev_note.note_number
                interval_dict[
                    portion.closedopen(
                        next_note.pos + next_event.portamento_offset,
                        next_note.pos
                        + next_event.portamento_offset
                        + next_event.portamento_length,
                    )
                ] = functools.partial(
                    cosine_easing_in_out_interpolation,
                    start=Point(
                        x=next_note.pos + next_event.portamento_offset,
                        y=prev_note.note_number,
                    ),
                    end=Point(
                        x=next_note.pos
                        + next_event.portamento_offset
                        + next_event.portamento_length,
                        y=next_note.note_number,
                    ),
                )
            else:
                interval_dict[
                    portion.closedopen(
                        prev_note.pos
                        + prev_event.portamento_offset
                        + prev_event.portamento_length,
                        prev_note.end_pos,
                    )
                ] = prev_note.note_number
            if is_last:
                interval_dict[
                    portion.closedopen(
                        next_note.pos
                        + next_event.portamento_offset
                        + next_event.portamento_length,
                        portion.inf,
                    )
                ] = next_note.note_number
    return interval_dict
