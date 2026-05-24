from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING

import portion

from libresvip.core.constants import TICKS_IN_BEAT
from libresvip.model.base import ParamCurve, Points
from libresvip.model.point import Point

if TYPE_CHECKING:
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
        all_tick_positions: list[int] = []
        tick_pos_to_idx: dict[int, int] = {}

        def _ensure_tick(tick_pos: int) -> None:
            if tick_pos not in tick_pos_to_idx:
                tick_pos_to_idx[tick_pos] = len(all_tick_positions)
                all_tick_positions.append(tick_pos)

        for point in points:
            pos = point.x + (0 if to_absolute else -self.first_bar_length)
            _ensure_tick(pos)

        prev_x = None
        prev_y_is_none = True
        for point in points:
            cur_x = point.x + (self.first_bar_length if to_absolute else -self.first_bar_length)
            # We don't know yet if base_key is None, but we optimistically collect
            # interpolation ticks. We'll filter later.
            if prev_x is not None and not prev_y_is_none and cur_x - prev_x > self.pitch_interval:
                for tick in range(prev_x + self.pitch_interval, cur_x, self.pitch_interval):
                    tick_pos = tick + (-self.first_bar_length if to_absolute else 0)
                    _ensure_tick(tick_pos)
            prev_x = cur_x
            # We can't fully determine prev_y_is_none without the pitch data,
            # so we conservatively assume it might not be None.
            # This means we may query a few extra ticks, but that's fine.
            prev_y_is_none = False

        # Phase 2: batch pitch lookup
        pitch_values: list[float | None]
        if all_tick_positions:
            pitch_values = pitch_simulator.pitch_at_ticks_batch(all_tick_positions)
        else:
            pitch_values = []

        # Phase 3: main conversion loop using pre-fetched pitch values
        converted_data: list[Point] = []
        prev_x = None
        prev_y: float | None = None
        for point in points:
            pos = point.x + (0 if to_absolute else -self.first_bar_length)
            cur_x = point.x + (self.first_bar_length if to_absolute else -self.first_bar_length)
            base_key = pitch_values[tick_pos_to_idx[pos]]
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
                for tick in range(prev_x + self.pitch_interval, cur_x, self.pitch_interval):
                    tick_pos = tick + (-self.first_bar_length if to_absolute else 0)
                    tick_key = pitch_values[tick_pos_to_idx[tick_pos]]
                    if tick_key is not None:
                        if to_absolute:
                            if self.is_staircase or rel_y is None:
                                interpolated_rel_y = prev_y
                            else:
                                interpolated_rel_y = prev_y + (rel_y - prev_y) * (tick - prev_x) / (
                                    cur_x - prev_x
                                )
                            converted_data.append(
                                Point(x=tick, y=round(interpolated_rel_y + tick_key))
                            )
                        elif not (self.is_staircase and prev_y == y):
                            converted_data.append(
                                Point(
                                    x=tick,
                                    y=round(
                                        prev_y + (y - prev_y) * (tick - prev_x) / (cur_x - prev_x)
                                    ),
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
