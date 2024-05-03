from __future__ import annotations

import dataclasses

import more_itertools
import portion

from libresvip.core.constants import TICKS_IN_BEAT
from libresvip.core.exceptions import NotesOverlappedError
from libresvip.core.time_interval import PiecewiseIntervalDict
from libresvip.model.base import Note, ParamCurve, Points
from libresvip.model.point import Point
from libresvip.utils.translation import gettext_lazy as _


def get_interval_dict(notes: list[Note], to_absolute: bool) -> PiecewiseIntervalDict:
    interval_dict = PiecewiseIntervalDict()
    for is_first, is_last, note in more_itertools.mark_ends(notes):
        if is_first and is_last:
            interval = portion.closed(note.start_pos, note.end_pos)
        elif is_first:
            interval = portion.closedopen(note.start_pos, note.end_pos)
        elif is_last:
            interval = portion.openclosed(note.start_pos, note.end_pos)
        else:
            interval = portion.open(note.start_pos, note.end_pos)
        if not interval.intersection(interval_dict.domain()).empty:
            msg = _("Notes Overlapped")
            raise NotesOverlappedError(msg)
        interval_dict[interval] = note.key_number
    for prev_note, next_note in more_itertools.windowed(notes, 2):
        if next_note is None:
            continue
        if prev_note.end_pos < next_note.start_pos:
            if next_note.lyric == "-":
                interval_dict[portion.singleton(prev_note.end_pos)] = (
                    prev_note.key_number + next_note.key_number
                ) / 2
                interval_dict[portion.openclosed(prev_note.end_pos, next_note.start_pos)] = (
                    next_note.key_number
                )
            else:
                middle_pos = (prev_note.end_pos + next_note.start_pos) / 2
                interval_dict[portion.closedopen(prev_note.end_pos, middle_pos)] = (
                    prev_note.key_number
                )
                interval_dict[portion.singleton(middle_pos)] = (
                    prev_note.key_number + next_note.key_number
                ) / 2
                interval_dict[portion.openclosed(middle_pos, next_note.start_pos)] = (
                    next_note.key_number
                )
        else:
            interval_dict[portion.singleton(next_note.start_pos)] = next_note.key_number
    return interval_dict


@dataclasses.dataclass
class RelativePitchCurve:
    first_bar_length: int = TICKS_IN_BEAT * 4
    lower_bound: float = 0.0
    upper_bound: float = portion.inf
    pitch_interval: int = 5

    def to_absolute(self, points: list[Point], note_list: list[Note]) -> ParamCurve:
        return ParamCurve(
            points=Points(root=self._convert_relativity(points, note_list, to_absolute=True))
        )

    def _convert_relativity(
        self,
        points: list[Point],
        note_list: list[Note],
        border_append_radius: int = 0,
        to_absolute: bool = False,
    ) -> list[Point]:
        converted_data: list[Point] = []
        if not len(note_list):
            return converted_data
        interval_dict = get_interval_dict(note_list, to_absolute)
        prev_x = None
        prev_y = None
        for point in points:
            pos = point.x + (0 if to_absolute else -self.first_bar_length)
            cur_x = point.x + (self.first_bar_length if to_absolute else -self.first_bar_length)
            if (base_key := interval_dict.get(pos)) is None:
                y = None
            elif not to_absolute and point.y == -100:
                y = 0
            else:
                y = point.y + (base_key if to_absolute else -base_key) * 100
            if (
                y is not None
                and prev_y is not None
                and converted_data
                and cur_x - prev_x > self.pitch_interval
            ):
                for tick in range(prev_x + self.pitch_interval, cur_x, self.pitch_interval):
                    tick_pos = tick + (-self.first_bar_length if to_absolute else 0)
                    if (tick_key := interval_dict.get(tick_pos)) is not None:
                        if to_absolute:
                            converted_data.append(Point(x=tick, y=round(prev_y + tick_key * 100)))
                        else:
                            converted_data.append(
                                Point(
                                    x=tick,
                                    y=prev_y + (y - prev_y) * (tick - prev_x) / (cur_x - prev_x),
                                )
                            )
            if y is not None:
                if to_absolute and prev_y is None:
                    converted_data.append(Point(x=cur_x, y=-100))
                cur_point = Point(x=cur_x, y=round(y))
                converted_data.append(cur_point)
                if to_absolute:
                    if point.y:
                        prev_y = point.y
                    else:
                        converted_data.append(Point(x=cur_x, y=-100))
                        prev_y = None
                else:
                    prev_y = None if point.y == -100 else y
            else:
                prev_y = None
            prev_x = cur_x
        if converted_data and to_absolute:
            if self.lower_bound == 0:
                converted_data.insert(0, Point.start_point())
            if self.upper_bound == portion.inf:
                converted_data.extend((converted_data[-1]._replace(y=-100), Point.end_point()))
        if not to_absolute:
            return self.append_points_at_borders(
                converted_data, note_list, radius=border_append_radius
            )
        return converted_data

    def from_absolute(
        self, points: list[Point], notes: list[Note], border_append_radius: int = 0
    ) -> list[Point]:
        return self._convert_relativity(points, notes, border_append_radius, to_absolute=False)

    def append_points_at_borders(
        self, data: list[Point], notes: list[Note], radius: int
    ) -> list[Point]:
        if radius <= 0:
            return data
        result = data.copy()
        for last_note, this_note in more_itertools.windowed(notes, 2):
            if this_note is None or this_note.start_pos - last_note.end_pos > radius:
                continue
            if (
                first_point_at_this_note_index := next(
                    (j for j, point in enumerate(result) if point.x >= this_note.start_pos),
                    None,
                )
            ) is not None:
                first_point_at_this_note = result[first_point_at_this_note_index]
                if first_point_at_this_note.x != this_note.start_pos:
                    # if first_point_at_this_note.x > this_note.start_pos + radius
                    post_value = first_point_at_this_note.y
                    new_point_tick = this_note.start_pos - radius
                    new_point = Point(x=new_point_tick, y=post_value)
                    result.insert(first_point_at_this_note_index, new_point)
                    result = [
                        point
                        for point in result
                        if not (
                            new_point_tick <= point.x < this_note.start_pos and point != new_point
                        )
                    ]
        return result
