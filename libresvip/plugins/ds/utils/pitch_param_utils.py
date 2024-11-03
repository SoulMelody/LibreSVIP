from typing import Optional

from libresvip.model.base import ParamCurve, Points
from libresvip.model.point import Point
from libresvip.utils.music_math import midi2hz

from ..models.ds_param_curve import DsParamCurve
from ..models.ds_param_node import DsParamNode


class PitchParamUtils:
    @classmethod
    def encode(cls, curve: ParamCurve, end: int, time_step: float = 0.005) -> DsParamCurve:
        end += 1920
        return DsParamCurve(
            step_size=time_step,
            point_list=cls.encode_point_list(curve.points, end),
        )

    @classmethod
    def encode_point_list(cls, os_point_list: Points, end: int) -> Optional[list[DsParamNode]]:
        if valid_points := [
            p for p in os_point_list.root if p.x >= 1930 and p.x + 10 < end and p.y >= 0
        ]:
            return [
                DsParamNode(
                    time=pos / 1000.0,
                    value=midi2hz(cls.value_at(valid_points, pos) / 100.0),
                )
                for pos in range(1920, end, 5)
            ]
        else:
            return None

    @staticmethod
    def value_at(segment: list[Point], ticks: float) -> float:
        left_point = next((p for p in reversed(segment) if p.x <= ticks), None)
        if left_point is None:
            return segment[0].y

        right_point = next((p for p in segment if p.x > ticks), None)
        if right_point is None:
            return segment[-1].y

        ratio = (ticks - left_point.x) / (right_point.x - left_point.x)
        return (1 - ratio) * left_point.y + ratio * right_point.y
