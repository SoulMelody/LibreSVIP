from libresvip.model.point import (
    Point,
    interpolate_cosine_ease_in,
    interpolate_cosine_ease_in_out,
    interpolate_cosine_ease_out,
    interpolate_linear,
)

from .model import UTAUPitchBendMode


def interpolate(
    last_point: Point,
    this_point: Point,
    curve_type: UTAUPitchBendMode,
    sampling_interval_tick: int,
) -> list[Point]:
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
