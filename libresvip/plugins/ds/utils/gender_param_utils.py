from libresvip.model.base import ParamCurve, Points
from libresvip.model.point import Point
from libresvip.utils.search import binary_find_first, binary_find_last

from ..models.ds_param_curve import DsParamCurve
from ..models.ds_param_node import DsParamNode


class GenderParamUtils:
    @classmethod
    def encode(cls, curve: ParamCurve, end: int, time_step: float = 0.005) -> DsParamCurve:
        end += 1920
        return DsParamCurve(
            step_size=time_step,
            point_list=cls.encode_point_list(curve.points, end),
        )

    @classmethod
    def encode_point_list(cls, os_point_list: Points, end: int) -> list[DsParamNode]:
        valid_points = [
            p for p in os_point_list.root if p.x >= 1930 and p.x + 10 < end and -1000 <= p.y <= 1000
        ]
        return [
            DsParamNode(
                time=pos / 1000.0,
                value=cls.value_at(valid_points, pos) / 1000.0,
            )
            for pos in range(1920, end, 5)
        ]

    @staticmethod
    def value_at(segment: list[Point], ticks: float) -> float:
        left_point = binary_find_last(segment, lambda point: point.x <= ticks)
        if left_point is None:
            return segment[0].y

        right_point = binary_find_first(segment, lambda point: point.x > ticks)
        if right_point is None:
            return segment[-1].y

        ratio = (ticks - left_point.x) / (right_point.x - left_point.x)
        return (1 - ratio) * left_point.y + ratio * right_point.y
