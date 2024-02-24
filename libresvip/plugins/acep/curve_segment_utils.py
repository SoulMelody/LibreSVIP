from libresvip.model.point import Point
from libresvip.utils.search import binary_find_first, binary_find_last


def get_value_from_segment(segment: list[Point], ticks: float) -> float:
    if (left_point := binary_find_last(segment, lambda point: point.x <= ticks)) is None:
        return segment[0].y
    if (right_point := binary_find_first(segment, lambda point: point.x > ticks)) is None:
        return segment[-1].y
    ratio = (ticks - left_point.x) / (right_point.x - left_point.x)
    return (1 - ratio) * left_point.y + ratio * right_point.y
