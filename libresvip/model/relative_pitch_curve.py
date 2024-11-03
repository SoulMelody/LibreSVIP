from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING, Optional

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
        converted_data: list[Point] = []
        prev_x = None
        prev_y: Optional[float] = None
        for point in points:
            pos = point.x + (0 if to_absolute else -self.first_bar_length)
            cur_x = point.x + (self.first_bar_length if to_absolute else -self.first_bar_length)
            if (base_key := pitch_simulator.pitch_at_ticks(pos)) is None:
                y = None
            elif not to_absolute and point.y == -100:
                if point.x in [-192000, 1073741823]:
                    continue
                y = 0.0
            else:
                y = point.y + (base_key if to_absolute else -base_key)
            if (
                y is not None
                and prev_x is not None
                and prev_y is not None
                and converted_data
                and cur_x - prev_x > self.pitch_interval
            ):
                for tick in range(prev_x + self.pitch_interval, cur_x, self.pitch_interval):
                    tick_pos = tick + (-self.first_bar_length if to_absolute else 0)
                    if (tick_key := pitch_simulator.pitch_at_ticks(tick_pos)) is not None:
                        if to_absolute:
                            converted_data.append(Point(x=tick, y=round(prev_y + tick_key)))
                        else:
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
        return converted_data

    def from_absolute(
        self,
        points: list[Point],
        pitch_simulator: PitchSimulator,
    ) -> list[Point]:
        return self._convert_relativity(points, pitch_simulator, to_absolute=False)
