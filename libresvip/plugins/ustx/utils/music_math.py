from libresvip.model.point import (
    cosine_easing_in_interpolation,
    cosine_easing_in_out_interpolation,
    cosine_easing_out_interpolation,
    linear_interpolation,
)


def interpolate_shape(
    start: tuple[float, float], end: tuple[float, float], x: float, shape: str
) -> float:
    if shape == "io":
        return cosine_easing_in_out_interpolation(start, end, x)
    elif shape == "i":
        return cosine_easing_in_interpolation(start, end, x)
    elif shape == "o":
        return cosine_easing_out_interpolation(start, end, x)
    else:
        return linear_interpolation(start, end, x)
