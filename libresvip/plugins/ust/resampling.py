from operator import attrgetter

from libresvip.model.point import Point


def resampled(
    data: list[Point], interval: int, interpolate_method: callable
) -> list[Point]:
    result = []
    left_bound = min(data, key=attrgetter("x")).x if data else 0
    right_bound = max(data, key=attrgetter("x")).x if data else 0
    for current in range(left_bound, right_bound + 1, interval):
        prev = next((p for p in reversed(data) if p.x <= current), None)
        next_ = next((p for p in data if p.x >= current), None)
        result.append(Point(x=current, y=interpolate_method(prev, next_, current)))
    return result


def dot_resampled(data: list[Point], interval: int) -> list[Point]:
    return resampled(
        data,
        interval,
        lambda prev, next_, _: prev[1] if prev and prev[1] is not None else next_[1],
    )
