from collections.abc import Callable
from operator import attrgetter

from more_itertools import locate, minmax, rlocate

from libresvip.model.point import Point


def resampled(
    data: list[Point],
    interval: int,
    interpolate_method: Callable[[Point, Point, int], float],
) -> list[Point]:
    result = []
    left_point, right_point = minmax(data, key=attrgetter("x"), default=(Point(0, 0), Point(0, 0)))
    for current in range(left_point.x, right_point.x + 1, interval):
        if (prev_index := next(rlocate(data, lambda p: p.x <= current), None)) is not None and (
            next_index := next(locate(data, lambda p: p.x >= current), None)
        ) is not None:
            result.append(
                Point(
                    x=current,
                    y=int(interpolate_method(data[prev_index], data[next_index], current)),
                )
            )
    return result


def dot_resampled(data: list[Point], interval: int) -> list[Point]:
    return resampled(
        data,
        interval,
        lambda prev, next_, _: prev[1] if prev and prev[1] is not None else next_[1],
    )
