from dataclasses import dataclass

from libresvip.model.point import Point
from libresvip.utils.music_math import linear_interpolation

from .controller_models import ControllerCurve, ControllerEvent
from .controller_registry import get_param_def


@dataclass
class SimpleControllerHandler:
    simplify: bool = True
    simplify_threshold: float = 1.0

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
