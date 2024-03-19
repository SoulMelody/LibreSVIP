import math

from libresvip.model.point import Point


def perpendicular_distance(pt: Point, line_start: Point, line_end: Point) -> float:
    dx: float = line_end.x - line_start.x
    dy: float = line_end.y - line_start.y

    # Normalize
    mag = math.hypot(dx, dy)
    if mag > 0.0:
        dx /= mag
        dy /= mag
    pvx = pt.x - line_start.x
    pvy = pt.y - line_start.y

    # Get dot product (project pv onto normalized direction)
    pvdot = dx * pvx + dy * pvy

    # Scale line direction vector and subtract it from pv
    ax = pvx - pvdot * dx
    ay = pvy - pvdot * dy

    return math.hypot(ax, ay)


def simplify_shape(point_list: list[Point], epsilon: float) -> list[Point]:
    if len(point_list) < 2:
        return point_list

    # Find the point with the maximum distance from line between start and end
    dmax = 0.0
    index = 0
    end = len(point_list) - 1
    for i in range(1, end):
        d = perpendicular_distance(point_list[i], point_list[0], point_list[end])
        if d > dmax:
            index = i
            dmax = d

    if dmax <= epsilon:
        # Just return start and end points
        return [point_list[0], point_list[-1]]
    first_line = point_list[: index + 1]
    last_line = point_list[index:]
    rec_results1 = simplify_shape(first_line, epsilon)
    rec_results2 = simplify_shape(last_line, epsilon)

    # build the result list
    return rec_results1[:-1] + rec_results2


def simplify_shape_to(point_list: list[Point], max_point_count: int) -> list[Point]:
    step = 0.05
    epsilon = step
    while True:
        result = simplify_shape(point_list, epsilon)
        if len(result) < max_point_count:
            return result
        epsilon += step
