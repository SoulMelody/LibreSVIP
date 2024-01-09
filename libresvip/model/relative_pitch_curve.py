from __future__ import annotations

import dataclasses
from bisect import bisect_right
from gettext import gettext as _

from more_itertools import pairwise

from libresvip.core.constants import TICKS_IN_BEAT
from libresvip.core.exceptions import NotesOverlappedError
from libresvip.model.base import Note, ParamCurve
from libresvip.model.point import Point


@dataclasses.dataclass
class RelativePitchCurve:
    first_bar_length: int = TICKS_IN_BEAT * 4

    def to_absolute(self, points: list[Point], note_list: list[Note]) -> ParamCurve:
        param_curve = ParamCurve()
        boundries = [(note.start_pos, note.end_pos) for note in note_list]
        prev_index = -1
        for point in points:
            note_index = bisect_right(boundries, (point.x, point.x)) - 1
            if note_index < 0:
                continue
            elif note_index > prev_index:
                prev_index = note_index
                if len(param_curve.points) > 0:
                    param_curve.points.append(Point(x=param_curve.points[-1].x, y=-100))
                else:
                    param_curve.points.append(Point.start_point())
                param_curve.points.append(Point(x=point.x + self.first_bar_length, y=-100))
            note = note_list[note_index]
            if not note.start_pos <= point.x < note.end_pos:
                continue
            y = note.key_number * 100 + point.y
            param_curve.points.append(Point(x=point.x + self.first_bar_length, y=y))
        if len(param_curve.points) > 0:
            param_curve.points.append(Point.end_point())
        return param_curve

    def from_absolute(
        self, pitch: ParamCurve, notes: list[Note], border_append_radius: int = 0
    ) -> list[Point]:
        if not notes:
            return []
        borders = self.get_borders(notes)
        index = 0
        current_note_key = notes[0].key_number
        next_border = borders[index] if index < len(borders) else float("inf")
        converted_data = []
        for pos, value in pitch.points.root:
            if value <= 0:
                continue
            while pos >= next_border:
                index += 1
                next_border = borders[index] if index < len(borders) else float("inf")
                current_note_key = notes[index].key_number
            converted_value = value - current_note_key * 100
            converted_data.append(Point(x=pos - self.first_bar_length, y=converted_value))
        return self.append_points_at_borders(converted_data, notes, radius=border_append_radius)

    def get_borders(self, notes: list[Note]) -> list[int]:
        borders = []
        pos = -1
        for note in notes:
            if pos < 0:
                pos = note.end_pos
                continue
            if pos == note.start_pos:
                borders.append(pos + self.first_bar_length)
            elif pos < note.start_pos:
                borders.append((note.start_pos + pos) // 2 + self.first_bar_length)
            else:
                msg = _("Notes Overlapped")
                raise NotesOverlappedError(msg)
            pos = note.end_pos
        return borders

    def append_points_at_borders(
        self, data: list[Point], notes: list[Note], radius: int
    ) -> list[Point]:
        if radius <= 0:
            return data
        result = data.copy()
        for last_note, this_note in pairwise(notes):
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
