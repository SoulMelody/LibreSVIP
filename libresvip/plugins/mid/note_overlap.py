from operator import attrgetter

from libresvip.core.time_interval import RangeInterval
from libresvip.model.base import Note


def has_overlap(notes: list[Note]) -> bool:
    if len(notes) < 2:
        return False
    notes.sort(key=attrgetter("start_pos"))
    interval = RangeInterval()
    for note in notes:
        if interval.includes(note.start_pos):
            return True
        interval |= RangeInterval([(note.start_pos, note.end_pos)])
    return False
