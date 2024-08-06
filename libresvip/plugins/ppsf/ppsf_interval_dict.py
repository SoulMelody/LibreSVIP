import functools

import more_itertools
import portion

from libresvip.core.time_interval import PiecewiseIntervalDict
from libresvip.model.point import Point
from libresvip.utils.music_math import cosine_easing_in_out_interpolation

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
        ) in more_itertools.mark_ends(more_itertools.pairwise(zip(event_list, note_list))):
            if is_first:
                interval_dict[
                    portion.closedopen(
                        0,
                        prev_note.pos + prev_event.portamento_offset + prev_event.portamento_length,
                    )
                ] = prev_note.note_number
            if next_event.portamento_length:
                if (
                    prev_portamento_end := prev_note.pos
                    + prev_event.portamento_offset
                    + prev_event.portamento_length
                ) < (next_portamento_start := next_note.pos + next_event.portamento_offset):
                    interval_dict[
                        portion.closedopen(
                            prev_portamento_end,
                            next_portamento_start,
                        )
                    ] = prev_note.note_number
                interval_dict[
                    portion.closedopen(
                        next_portamento_start,
                        next_note.pos + next_event.portamento_offset + next_event.portamento_length,
                    )
                ] = functools.partial(
                    cosine_easing_in_out_interpolation,  # type: ignore[call-arg]
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
            elif (
                prev_portamento_end := prev_note.pos
                + prev_event.portamento_offset
                + prev_event.portamento_length
            ) < prev_note.end_pos:
                interval_dict[
                    portion.closedopen(
                        prev_portamento_end,
                        prev_note.end_pos,
                    )
                ] = prev_note.note_number
            if is_last:
                interval_dict[
                    portion.closedopen(
                        next_note.pos + next_event.portamento_offset + next_event.portamento_length,
                        portion.inf,
                    )
                ] = next_note.note_number
    return interval_dict
