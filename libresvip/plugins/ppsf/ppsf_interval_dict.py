import functools
import itertools

import more_itertools
import portion

from libresvip.core.time_interval import PiecewiseIntervalDict
from libresvip.model.point import Point

from .model import PpsfDvlTrackEvent, PpsfNote
from .portamento import glide_interpolation, portamento_span


def _note_span(event: PpsfDvlTrackEvent, note: PpsfNote) -> tuple[int, int]:
    return portamento_span(
        event.pos,
        note.portamento_offset or 0,
        note.portamento_length or 0,
    )


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
            ((prev_event, prev_note), (next_event, next_note)),
        ) in more_itertools.mark_ends(itertools.pairwise(zip(event_list, note_list))):
            _, prev_end = _note_span(prev_event, prev_note)
            if is_first:
                interval_dict[portion.closedopen(0, prev_end)] = prev_event.note_number
            if next_note.portamento_length:
                next_start, next_end = _note_span(next_event, next_note)
                if prev_end < next_start:
                    interval_dict[portion.closedopen(prev_end, next_start)] = prev_event.note_number
                interval_dict[portion.closedopen(next_start, next_end)] = functools.partial(
                    glide_interpolation(next_event.portamento_type),
                    start=Point(x=next_start, y=prev_event.note_number),
                    end=Point(x=next_end, y=next_event.note_number),
                )
            elif prev_end < prev_event.end_pos:
                interval_dict[portion.closedopen(prev_end, prev_event.end_pos)] = (
                    prev_event.note_number
                )
            if is_last:
                _, last_end = _note_span(next_event, next_note)
                interval_dict[portion.closedopen(last_end, portion.inf)] = next_event.note_number
    return interval_dict
