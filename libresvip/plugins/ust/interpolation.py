import math
from functools import partial

from pkg_resources.extern.more_itertools import pairwise

from libresvip.model.point import Point

from .model import UTAUPitchBendMode


def interpolate(last_point: Point, this_point: Point, curve_type: UTAUPitchBendMode, sampling_interval_tick: int) -> list[Point]:
    input_data = [last_point, this_point]
    if curve_type == "s":
        output = interpolate_linear(input_data, sampling_interval_tick)
    elif curve_type == "j":
        output = interpolate_cosine_ease_in(input_data, sampling_interval_tick)
    elif curve_type == "r":
        output = interpolate_cosine_ease_out(input_data, sampling_interval_tick)
    else:
        output = interpolate_cosine_ease_in_out(input_data, sampling_interval_tick)
    return output

def _inner_interpolate(data: list[Point], sampling_interval_tick: int, mapping: callable) -> list[Point]:
    return data if not data else [data[0]] + [
        point for start, end in pairwise(data)
        for point in mapping(start, end, range(start.x + 1, end.x))
        if (point.x - start.x) % sampling_interval_tick == 0
    ] + [data[-1]]

def _linear_mapping(start: Point, end: Point, indexes: list[int]) -> list[Point]:
    x0, y0 = start.x, start.y
    x1, y1 = end.x, end.y
    return [Point(x=x, y=round(y0 + (x - x0) * (y1 - y0) / (x1 - x0))) for x in indexes]

interpolate_linear = partial(_inner_interpolate, mapping=_linear_mapping)


def _cosine_ease_in_out_mapping(start: Point, end: Point, indexes: list[int]) -> list[Point]:
    x0, y0 = start.x, start.y
    x1, y1 = end.x, end.y
    x_offset = x0
    y_offset = (y0 + y1) / 2
    a_freq = math.pi / (x1 - x0)
    amp = (y0 - y1) / 2
    return [Point(x=x, y=round(amp * math.cos(a_freq * (x - x_offset)) + y_offset)) for x in indexes]

interpolate_cosine_ease_in_out = partial(_inner_interpolate, mapping=_cosine_ease_in_out_mapping)


def _cosine_ease_in_mapping(start: Point, end: Point, indexes: list[int]) -> list[Point]:
    x0, y0 = start.x, start.y
    x1, y1 = end.x, end.y
    x_offset = x0
    y_offset = y1
    a_freq = math.pi / (x1 - x0) / 2
    amp = y0 - y1
    return [Point(x=x, y=round(amp * math.cos(a_freq * (x - x_offset)) + y_offset)) for x in indexes]

interpolate_cosine_ease_in = partial(_inner_interpolate, mapping=_cosine_ease_in_mapping)


def _cosine_ease_out_mapping(start: Point, end: Point, indexes: list[int]) -> list[Point]:
    x0, y0 = start.x, start.y
    x1, y1 = end.x, end.y
    x_offset = x0
    y_offset = y0
    a_freq = math.pi / (x1 - x0) / 2
    amp = y0 - y1
    phase = math.pi / 2
    return [Point(x=x, y=round(amp * math.cos(a_freq * (x - x_offset) + phase) + y_offset)) for x in indexes]

interpolate_cosine_ease_out = partial(_inner_interpolate, mapping=_cosine_ease_out_mapping)
