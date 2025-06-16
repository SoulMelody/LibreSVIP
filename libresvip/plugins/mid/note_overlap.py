from operator import attrgetter

from libresvip.core.time_interval import RangeInterval
from libresvip.model.base import Note


def overlapped_pos(notes: list[Note]) -> int | None:
    if len(notes) < 2:
        return None
    notes.sort(key=attrgetter("start_pos"))
    interval = RangeInterval()
    for note in notes:
        if interval.includes(note.start_pos):
            return note.start_pos
        interval |= RangeInterval([(note.start_pos, note.end_pos)])
    return None
