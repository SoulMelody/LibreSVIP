from __future__ import annotations

from bisect import bisect_right
from typing import Optional

from more_itertools import pairwise

from libresvip.model.base import Note, ParamCurve, Points
from libresvip.model.point import Point


class RelativePitchCurve(ParamCurve):

    def to_absolute(self, note_list: list[Note]) -> ParamCurve:
        param_curve = ParamCurve()
        boundries = [(note.start_pos, note.end_pos) for note in note_list]
        prev_index = -1
        for point in self.points:
            note_index = bisect_right(boundries, (point.x, point.x)) - 1
            if note_index < 0:
                continue
            elif note_index > prev_index:
                prev_index = note_index
                if len(param_curve.points) > 0:
                    param_curve.points.append(Point(x=param_curve.points[-1].x, y=-100))
                else:
                    param_curve.points.append(Point.start_point())
                param_curve.points.append(Point(x=point.x + 1920, y=-100))
            note = note_list[note_index]
            if not note.start_pos <= point.x < note.end_pos:
                continue
            y = note.key_number * 100 + point.y
            param_curve.points.append(Point(x=point.x + 1920, y=y))
        if len(param_curve.points) > 0:
            param_curve.points.append(Point.end_point())
        return param_curve

    @classmethod
    def from_absolute(
        cls, pitch: ParamCurve, notes: list[Note], border_append_radius: int = 0
    ) -> Optional[RelativePitchCurve]:
        if not notes:
            return None
        borders = cls.get_borders(notes)
        index = 0
        current_note_key = notes[0].key_number
        next_border = borders[index] if index < len(borders) else float("inf")
        converted_data = []
        for pos, value in pitch.points:
            if value <= 0:
                continue
            while pos >= next_border:
                index += 1
                next_border = borders[index] if index < len(borders) else float("inf")
                current_note_key = notes[index].key_number
            converted_value = value - current_note_key * 100
            converted_data.append(Point(x=pos - 1920, y=converted_value))
        point_list = cls.append_points_at_borders(
            converted_data, notes, radius=border_append_radius
        )
        return cls(points=Points(root=point_list))

    @staticmethod
    def get_borders(notes: list[Note]) -> list[int]:
        borders = []
        pos = -1
        for note in notes:
            if pos < 0:
                pos = note.end_pos
                continue
            if pos == note.start_pos:
                borders.append(pos + 1920)
            elif pos < note.start_pos:
                borders.append((note.start_pos + pos) // 2 + 1920)
            else:
                raise Exception("Notes Overlapped")
            pos = note.end_pos
        return borders

    @staticmethod
    def append_points_at_borders(
        data: list[Point], notes: list[Note], radius: int
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
                        if point.x >= this_note.start_pos + 1920
                    ),
                    None,
                )
            ) is None:
                continue
            first_point_at_this_note = result[first_point_at_this_note_index]
            if (
                first_point_at_this_note.x == this_note.start_pos + 1920
                or first_point_at_this_note.x > this_note.start_pos + radius + 1920
            ):
                continue
            post_value = first_point_at_this_note.y
            new_point_tick = this_note.start_pos + 1920 - radius
            new_point = Point(x=new_point_tick, y=post_value)
            result.insert(first_point_at_this_note_index, new_point)
            result = [
                point
                for point in result
                if not (
                    new_point_tick <= point.x < this_note.start_pos + 1920
                    and point != new_point
                )
            ]
        return result
