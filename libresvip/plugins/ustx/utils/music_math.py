from libresvip.model.point import (
    linear_interpolation,
    sin_easing_in_interpolation,
    sin_easing_in_out_interpolation,
    sin_easing_out_interpolation,
)


def interpolate_shape(
    start: tuple[float, float], end: tuple[float, float], x: float, shape: str
) -> float:
    if shape == "io":
        return sin_easing_in_out_interpolation(start, end, x)
    elif shape == "i":
        return sin_easing_in_interpolation(start, end, x)
    elif shape == "o":
        return sin_easing_out_interpolation(start, end, x)
    else:
        return linear_interpolation(start, end, x)
