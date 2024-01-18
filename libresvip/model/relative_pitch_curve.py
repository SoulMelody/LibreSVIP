from __future__ import annotations

import dataclasses
from gettext import gettext as _

from more_itertools import pairwise

from libresvip.core.constants import TICKS_IN_BEAT
from libresvip.core.exceptions import NotesOverlappedError
from libresvip.model.base import Note, ParamCurve, Points
from libresvip.model.point import Point


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
        borders = self.get_borders(note_list)
        note_index, prev_index = 0, -1
        current_note = note_list[note_index]
        next_border = borders[note_index] if note_index < len(borders) else float("inf")
        for point in points:
            while point.x >= next_border:
                note_index += 1
                next_border = borders[note_index] if note_index < len(borders) else float("inf")
                current_note = note_list[note_index]
            if note_index < 0:
                continue
            elif note_index > prev_index:
                prev_index = note_index
                if to_absolute:
                    if len(converted_data) > 0:
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
            if not current_note.start_pos <= point.x < current_note.end_pos:
                continue
            elif not to_absolute and point.y == -100:
                continue
            y = (
                point.y
                + (current_note.key_number if to_absolute else -current_note.key_number) * 100
            )
            converted_data.append(
                Point(
                    x=point.x + (self.first_bar_length if to_absolute else -self.first_bar_length),
                    y=y,
                )
            )
        if len(converted_data) > 0 and to_absolute:
            converted_data.append(Point.end_point())
        return self.append_points_at_borders(converted_data, note_list, radius=border_append_radius)

    def from_absolute(
        self, pitch: ParamCurve, notes: list[Note], border_append_radius: int = 0
    ) -> list[Point]:
        return self._convert_relativity(
            pitch.points.root, notes, border_append_radius, to_absolute=False
        )

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
