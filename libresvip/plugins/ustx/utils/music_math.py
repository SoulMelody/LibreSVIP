from libresvip.utils.music_math import (
    cosine_easing_in_interpolation,
    cosine_easing_in_out_interpolation,
    cosine_easing_out_interpolation,
    linear_interpolation,
)


def interpolate_shape(
    start: tuple[float, float], end: tuple[float, float], x: float, shape: str
) -> float:
    if shape == "io":
        return cosine_easing_in_out_interpolation(x, start, end)
    elif shape == "i":
        return cosine_easing_in_interpolation(x, start, end)
    elif shape == "o":
        return cosine_easing_out_interpolation(x, start, end)
    else:
        return linear_interpolation(x, start, end)
