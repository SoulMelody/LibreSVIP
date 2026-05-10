from dataclasses import dataclass

from libresvip.model.point import Point
from libresvip.utils.music_math import clamp

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

        points: list[Point] = []
        previous_value = round(curve.default_value * value_scale + value_offset)

        for event in curve.events:
            current_value = round(event.value * value_scale + value_offset)
            self._append_step_points(points, event.pos, previous_value, current_value)
            previous_value = current_value

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
            value = int(clamp(point.y, min_val, max_val))
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
        reverse_value: bool = False,
    ) -> list[Point]:
        if curve.is_empty():
            return []
        points: list[Point] = []
        previous_value = self._map_external_to_internal(
            curve.default_value,
            curve.default_value,
            curve.min_value,
            curve.max_value,
            reverse=reverse_value,
        )
        for event in curve.events:
            current_pos = event.pos + position_offset
            current_value = self._map_external_to_internal(
                event.value,
                curve.default_value,
                curve.min_value,
                curve.max_value,
                reverse=reverse_value,
            )
            self._append_step_points(points, current_pos, previous_value, current_value)
            previous_value = current_value
        return points

    def convert_param_points_to_vocaloid_curve(
        self,
        points: list[Point],
        param_name: str,
        position_offset: int = 0,
        default_value: int | None = None,
        min_value: int | None = None,
        max_value: int | None = None,
        reverse_value: bool = False,
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
        else:
            real_points = self._collapse_step_points(real_points)
        events = [
            ControllerEvent(
                pos=point.x + position_offset,
                value=self._map_internal_to_external(
                    point.y,
                    default_val,
                    min_val,
                    max_val,
                    reverse=reverse_value,
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

        return self._collapse_step_points(points)

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
        reverse: bool = False,
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
        if reverse:
            mapped_value = -mapped_value
        return max(self.internal_min_value, min(self.internal_max_value, mapped_value))

    def _map_internal_to_external(
        self,
        value: int,
        default_value: int,
        min_value: int,
        max_value: int,
        reverse: bool = False,
    ) -> int:
        clamped_value = max(self.internal_min_value, min(self.internal_max_value, value))
        if reverse:
            clamped_value = -clamped_value
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

    @staticmethod
    def _append_step_points(
        points: list[Point],
        current_pos: int,
        previous_value: int,
        current_value: int,
    ) -> None:
        boundary_pos = current_pos - 1
        if current_value != previous_value and boundary_pos >= 0:
            boundary_point = Point(x=boundary_pos, y=previous_value)
            if not points or points[-1] != boundary_point:
                points.append(boundary_point)
        current_point = Point(x=current_pos, y=current_value)
        if not points or points[-1] != current_point:
            points.append(current_point)

    @staticmethod
    def _collapse_step_points(points: list[Point]) -> list[Point]:
        if len(points) <= 2:
            return points

        result: list[Point] = []
        i = 0
        while i < len(points):
            point = points[i]
            next_point = points[i + 1] if i + 1 < len(points) else None
            if (
                next_point is not None
                and next_point.x == point.x + 1
                and next_point.y != point.y
                and (
                    (i == 0 and point.y == 0)
                    or any(previous_point.y == point.y for previous_point in result)
                )
            ):
                result.append(next_point)
                i += 2
                continue
            if not result or result[-1] != point:
                result.append(point)
            i += 1
        return result


def convert_vocaloid_curve_to_param_points(
    curve: ControllerCurve,
    position_offset: int = 0,
    reverse_value: bool = False,
) -> list[Point]:
    handler = SimpleControllerHandler()
    return handler.convert_vocaloid_curve_to_param_points(curve, position_offset, reverse_value)


def convert_param_points_to_vocaloid_curve(
    points: list[Point],
    param_name: str,
    position_offset: int = 0,
    default_value: int | None = None,
    min_value: int | None = None,
    max_value: int | None = None,
    reverse_value: bool = False,
) -> ControllerCurve:
    handler = SimpleControllerHandler(simplify=False)
    return handler.convert_param_points_to_vocaloid_curve(
        points,
        param_name,
        position_offset,
        default_value,
        min_value,
        max_value,
        reverse_value,
    )
