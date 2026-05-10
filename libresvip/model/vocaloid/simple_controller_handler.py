from dataclasses import dataclass

from libresvip.model.point import Point
from libresvip.utils.music_math import linear_interpolation

from .controller_models import ControllerCurve, ControllerEvent
from .controller_registry import get_param_def


@dataclass
class SimpleControllerHandler:
    simplify: bool = True
    simplify_threshold: float = 1.0
    internal_min_value: int = -1000
    internal_max_value: int = 1000
    internal_default_value: int = 0

    def convert_to_points(
        self,
        curve: ControllerCurve,
        value_scale: float = 1.0,
        value_offset: float = 0.0,
    ) -> list[Point]:
        if curve.is_empty():
            return []

        points = []

        for i, event in enumerate(curve.events):
            converted_value = event.value * value_scale + value_offset

            if i > 0 and event.pos > curve.events[i - 1].pos + 1:
                points.append(Point(x=event.pos, y=round(converted_value)))
            else:
                points.append(Point(x=event.pos, y=round(converted_value)))

        return points

    def convert_from_points(
        self,
        points: list[Point],
        param_name: str,
    ) -> ControllerCurve:
        if not points:
            return ControllerCurve(name=param_name, events=[])

        param_def = get_param_def(param_name)
        min_val = param_def.min_value if param_def else -127
        max_val = param_def.max_value if param_def else 127
        default_val = param_def.default_value if param_def else 0

        if self.simplify and len(points) > 2:
            points = self._simplify_points(points, self.simplify_threshold)

        events = []
        for point in points:
            value = int(max(min_val, min(max_val, point.y)))
            events.append(ControllerEvent(pos=point.x, value=value))

        return ControllerCurve(
            name=param_name,
            events=events,
            default_value=default_val,
            min_value=min_val,
            max_value=max_val,
        )

    def convert_vocaloid_curve_to_param_points(
        self,
        curve: ControllerCurve,
        position_offset: int = 0,
    ) -> list[Point]:
        if curve.is_empty():
            return []
        return [
            Point(
                x=event.pos + position_offset,
                y=self._map_external_to_internal(
                    event.value,
                    curve.default_value,
                    curve.min_value,
                    curve.max_value,
                ),
            )
            for event in curve.events
        ]

    def convert_param_points_to_vocaloid_curve(
        self,
        points: list[Point],
        param_name: str,
        position_offset: int = 0,
        default_value: int | None = None,
        min_value: int | None = None,
        max_value: int | None = None,
    ) -> ControllerCurve:
        param_def = get_param_def(param_name)
        default_val = (
            default_value
            if default_value is not None
            else param_def.default_value
            if param_def is not None
            else 0
        )
        min_val = (
            min_value
            if min_value is not None
            else param_def.min_value
            if param_def is not None
            else -127
        )
        max_val = (
            max_value
            if max_value is not None
            else param_def.max_value
            if param_def is not None
            else 127
        )
        real_points = [point for point in points if self._is_real_point(point)]
        if self.simplify and len(real_points) > 2:
            real_points = self._simplify_points(real_points, self.simplify_threshold)
        events = [
            ControllerEvent(
                pos=point.x + position_offset,
                value=self._map_internal_to_external(
                    point.y,
                    default_val,
                    min_val,
                    max_val,
                ),
            )
            for point in real_points
        ]
        return ControllerCurve(
            name=param_name,
            events=events,
            default_value=default_val,
            min_value=min_val,
            max_value=max_val,
        )

    def _simplify_points(self, points: list[Point], threshold: float) -> list[Point]:
        if len(points) <= 2:
            return points

        result = [points[0]]

        for i in range(1, len(points) - 1):
            prev = result[-1]
            curr = points[i]
            next_point = points[i + 1]

            if next_point.x > prev.x:
                interpolated_y = linear_interpolation(
                    curr.x, (prev.x, prev.y), (next_point.x, next_point.y)
                )

                if abs(curr.y - interpolated_y) > threshold:
                    result.append(curr)
            else:
                result.append(curr)

        result.append(points[-1])
        return result

    def interpolate_curve(
        self,
        curve: ControllerCurve,
        start_pos: int,
        end_pos: int,
        step: int = 5,
    ) -> list[Point]:
        points = []
        current_pos = start_pos

        while current_pos <= end_pos:
            value = curve.get_value_at(current_pos)
            points.append(Point(x=current_pos, y=value))
            current_pos += step

        return points

    def _map_external_to_internal(
        self,
        value: int,
        default_value: int,
        min_value: int,
        max_value: int,
    ) -> int:
        if value >= default_value:
            denominator = max_value - default_value
            mapped_value = (
                self.internal_default_value
                if denominator == 0
                else round(
                    (value - default_value)
                    / denominator
                    * (self.internal_max_value - self.internal_default_value)
                    + self.internal_default_value
                )
            )
        else:
            denominator = default_value - min_value
            mapped_value = (
                self.internal_default_value
                if denominator == 0
                else round(
                    (value - default_value)
                    / denominator
                    * (self.internal_default_value - self.internal_min_value)
                    + self.internal_default_value
                )
            )
        return max(self.internal_min_value, min(self.internal_max_value, mapped_value))

    def _map_internal_to_external(
        self,
        value: int,
        default_value: int,
        min_value: int,
        max_value: int,
    ) -> int:
        clamped_value = max(self.internal_min_value, min(self.internal_max_value, value))
        if clamped_value >= self.internal_default_value:
            denominator = self.internal_max_value - self.internal_default_value
            mapped_value = (
                default_value
                if denominator == 0
                else round(
                    (clamped_value - self.internal_default_value)
                    / denominator
                    * (max_value - default_value)
                    + default_value
                )
            )
        else:
            denominator = self.internal_default_value - self.internal_min_value
            mapped_value = (
                default_value
                if denominator == 0
                else round(
                    (clamped_value - self.internal_default_value)
                    / denominator
                    * (default_value - min_value)
                    + default_value
                )
            )
        return max(min_value, min(max_value, mapped_value))

    @staticmethod
    def _is_real_point(point: Point) -> bool:
        return point.x not in {Point.start_point().x, Point.end_point().x}


def convert_dynamics_to_points(curve: ControllerCurve) -> list[Point]:
    handler = SimpleControllerHandler()
    return handler.convert_to_points(curve)


def convert_breathiness_to_points(curve: ControllerCurve) -> list[Point]:
    handler = SimpleControllerHandler()
    return handler.convert_to_points(curve)


def convert_brightness_to_points(curve: ControllerCurve) -> list[Point]:
    handler = SimpleControllerHandler()
    return handler.convert_to_points(curve)


def convert_gender_to_points(curve: ControllerCurve) -> list[Point]:
    handler = SimpleControllerHandler()
    return handler.convert_to_points(curve)


def convert_vocaloid_curve_to_param_points(
    curve: ControllerCurve,
    position_offset: int = 0,
) -> list[Point]:
    handler = SimpleControllerHandler()
    return handler.convert_vocaloid_curve_to_param_points(curve, position_offset)


def convert_param_points_to_vocaloid_curve(
    points: list[Point],
    param_name: str,
    position_offset: int = 0,
    default_value: int | None = None,
    min_value: int | None = None,
    max_value: int | None = None,
) -> ControllerCurve:
    handler = SimpleControllerHandler(simplify=False)
    return handler.convert_param_points_to_vocaloid_curve(
        points,
        param_name,
        position_offset,
        default_value,
        min_value,
        max_value,
    )
