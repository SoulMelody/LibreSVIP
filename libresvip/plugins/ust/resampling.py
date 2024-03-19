from collections.abc import Callable
from operator import attrgetter

from more_itertools import minmax

from libresvip.model.point import Point
from libresvip.utils.search import find_index, find_last_index


def resampled(
    data: list[Point],
    interval: int,
    interpolate_method: Callable[[Point, Point, int], float],
) -> list[Point]:
    left_point, right_point = minmax(data, key=attrgetter("x"), default=(Point(0, 0), Point(0, 0)))
    return [
        Point(
            x=current,
            y=int(interpolate_method(data[prev_index], data[next_index], current)),
        )
        for current in range(left_point.x, right_point.x + 1, interval)
        if (prev_index := find_last_index(data, lambda p: p.x <= current)) != -1
        and (next_index := find_index(data, lambda p: p.x >= current)) != -1
    ]


def dot_resampled(data: list[Point], interval: int) -> list[Point]:
    return resampled(
        data,
        interval,
        lambda prev, next_, _: prev[1] if prev and prev[1] is not None else next_[1],
    )
