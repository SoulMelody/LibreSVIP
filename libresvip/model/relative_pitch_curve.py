from __future__ import annotations

import dataclasses
import functools

import more_itertools
import portion

from libresvip.core.constants import TICKS_IN_BEAT
from libresvip.core.exceptions import NotesOverlappedError
from libresvip.core.time_interval import PiecewiseIntervalDict
from libresvip.model.base import Note, ParamCurve, Points
from libresvip.model.point import Point
from libresvip.utils.music_math import cosine_easing_in_out_interpolation
from libresvip.utils.translation import gettext_lazy as _


@dataclasses.dataclass
class RelativePitchCurve:
    first_bar_length: int = TICKS_IN_BEAT * 4

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
        interval_dict = self.get_interval_dict(note_list)
        note_index, prev_index = 0, -1
        for point in points:
            if note_index < 0:
                continue
            elif note_index > prev_index:
                prev_index = note_index
                if to_absolute:
                    if converted_data:
                        converted_data.append(Point(x=converted_data[-1].x, y=-100))
                    else:
                        converted_data.append(Point.start_point())
                    converted_data.append(
                        Point(
                            x=point.x
                            + (self.first_bar_length if to_absolute else -self.first_bar_length),
                            y=-100,
                        )
                    )
            if not to_absolute and point.y == -100:
                continue
            pos = point.x + (0 if to_absolute else -self.first_bar_length)
            if base_key := interval_dict.get(pos):
                y = point.y + (base_key if to_absolute else -base_key) * 100
                converted_data.append(
                    Point(
                        x=point.x
                        + (self.first_bar_length if to_absolute else -self.first_bar_length),
                        y=round(y),
                    )
                )
            if pos >= note_list[note_index].end_pos and note_index < len(note_list) - 1:
                note_index += 1
        if converted_data and to_absolute:
            converted_data.extend((Point(x=converted_data[-1].x, y=-100), Point.end_point()))
        return self.append_points_at_borders(converted_data, note_list, radius=border_append_radius)

    def from_absolute(
        self, points: list[Point], notes: list[Note], border_append_radius: int = 0
    ) -> list[Point]:
        return self._convert_relativity(points, notes, border_append_radius, to_absolute=False)

    def get_interval_dict(self, notes: list[Note]) -> PiecewiseIntervalDict:
        interval_dict = PiecewiseIntervalDict()
        for is_first, is_last, note in more_itertools.mark_ends(notes):
            if is_first and is_last:
                interval = portion.closedopen(0, portion.inf)
            elif is_first:
                interval = portion.closedopen(0, note.end_pos)
            elif is_last:
                interval = portion.closedopen(note.start_pos, portion.inf)
            else:
                interval = portion.closedopen(note.start_pos, note.end_pos)
            if not interval.intersection(interval_dict.domain()).empty:
                msg = _("Notes Overlapped")
                raise NotesOverlappedError(msg)
            interval_dict[interval] = note.key_number
        for prev_note, next_note in more_itertools.pairwise(notes):
            if prev_note.end_pos < next_note.start_pos:
                interval_dict[
                    portion.closedopen(prev_note.end_pos, next_note.start_pos)
                ] = functools.partial(
                    cosine_easing_in_out_interpolation,
                    start=(prev_note.end_pos, prev_note.key_number),
                    end=(next_note.start_pos, next_note.key_number),
                )
        return interval_dict

    def append_points_at_borders(
        self, data: list[Point], notes: list[Note], radius: int
    ) -> list[Point]:
        if radius <= 0:
            return data
        result = data.copy()
        for last_note, this_note in more_itertools.pairwise(notes):
            if this_note.start_pos - last_note.end_pos > radius:
                continue
            if (
                first_point_at_this_note_index := next(
                    (
                        j
                        for j, point in enumerate(result)
                        if point.x >= this_note.start_pos + self.first_bar_length
                    ),
                    None,
                )
            ) is None:
                continue
            first_point_at_this_note = result[first_point_at_this_note_index]
            if (
                first_point_at_this_note.x == this_note.start_pos + self.first_bar_length
                or first_point_at_this_note.x > this_note.start_pos + radius + self.first_bar_length
            ):
                continue
            post_value = first_point_at_this_note.y
            new_point_tick = this_note.start_pos + self.first_bar_length - radius
            new_point = Point(x=new_point_tick, y=post_value)
            result.insert(first_point_at_this_note_index, new_point)
            result = [
                point
                for point in result
                if not (
                    new_point_tick <= point.x < this_note.start_pos + self.first_bar_length
                    and point != new_point
                )
            ]
        return result
