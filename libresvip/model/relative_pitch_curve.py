from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING

import portion

from libresvip.core.constants import TICKS_IN_BEAT
from libresvip.model.base import ParamCurve, Points
from libresvip.model.point import Point

if TYPE_CHECKING:
    from collections.abc import Iterator

    from libresvip.model.pitch_simulator import PitchSimulator


@dataclasses.dataclass
class RelativePitchCurve:
    first_bar_length: int = TICKS_IN_BEAT * 4
    lower_bound: float = 0.0
    upper_bound: float = portion.inf
    pitch_interval: int = 5
    is_staircase: bool = True

    def to_absolute(self, points: list[Point], pitch_simulator: PitchSimulator) -> ParamCurve:
        return ParamCurve(
            points=Points(root=self._convert_relativity(points, pitch_simulator, to_absolute=True))
        )

    def _convert_relativity(
        self,
        points: list[Point],
        pitch_simulator: PitchSimulator,
        to_absolute: bool = False,
    ) -> list[Point]:
        pitch_offset = -self.first_bar_length if not to_absolute else 0
        converted_offset = self.first_bar_length if to_absolute else -self.first_bar_length
        point_tick_positions = [point.x + pitch_offset for point in points]
        pitch_values = pitch_simulator.pitch_at_ticks_batch(point_tick_positions)
        pitch_value_map: dict[int, float | None] = dict(zip(point_tick_positions, pitch_values))

        def get_pitch_value(tick_pos: int) -> float | None:
            if tick_pos not in pitch_value_map:
                pitch_value_map[tick_pos] = pitch_simulator.pitch_at_ticks(tick_pos)
            return pitch_value_map[tick_pos]

        def iter_interpolated_pitches(
            start_tick: int, end_tick: int
        ) -> Iterator[tuple[int, float | None]]:
            for tick in range(start_tick + self.pitch_interval, end_tick, self.pitch_interval):
                yield tick, get_pitch_value(tick - self.first_bar_length if to_absolute else tick)

        converted_data: list[Point] = []
        prev_x = None
        prev_y: float | None = None
        for point in points:
            pos = point.x + pitch_offset
            cur_x = point.x + converted_offset
            base_key = get_pitch_value(pos)
            if base_key is None:
                y = None
                rel_y = None
            elif not to_absolute and point.y == -100:
                if point.x in [-192000, 1073741823]:
                    continue
                y = 0.0
                rel_y = y
            else:
                rel_y = float(point.y) if to_absolute else point.y - base_key
                y = rel_y + base_key if to_absolute else rel_y
            if (
                y is not None
                and prev_x is not None
                and prev_y is not None
                and converted_data
                and cur_x - prev_x > self.pitch_interval
            ):
                for tick, tick_key in iter_interpolated_pitches(prev_x, cur_x):
                    if tick_key is None:
                        break
                    if to_absolute:
                        if self.is_staircase or rel_y is None:
                            interpolated_rel_y = prev_y
                        else:
                            interpolated_rel_y = prev_y + (rel_y - prev_y) * (tick - prev_x) / (
                                cur_x - prev_x
                            )
                        converted_data.append(Point(x=tick, y=round(interpolated_rel_y + tick_key)))
                    elif not (self.is_staircase and prev_y == y):
                        converted_data.append(
                            Point(
                                x=tick,
                                y=round(prev_y + (y - prev_y) * (tick - prev_x) / (cur_x - prev_x)),
                            )
                        )
            if y is not None:
                if to_absolute and prev_y is None:
                    converted_data.append(Point(x=cur_x, y=-100))
                cur_point = Point(x=cur_x, y=round(y))
                converted_data.append(cur_point)
                if to_absolute:
                    if point.y:
                        prev_y = rel_y
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
        return converted_data

    def from_absolute(
        self,
        points: list[Point],
        pitch_simulator: PitchSimulator,
    ) -> list[Point]:
        return self._convert_relativity(points, pitch_simulator, to_absolute=False)
