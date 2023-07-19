import math


def sin_easing_in_out(x0: float, x1: float, y0: float, y1: float, x: float) -> float:
    return y0 + (y1 - y0) * (1 - math.cos((x - x0) / (x1 - x0) * math.pi)) / 2

def sin_easing_in(x0: float, x1: float, y0: float, y1: float, x: float) -> float:
    return y0 + (y1 - y0) * (1 - math.cos((x - x0) / (x1 - x0) * math.pi / 2))

def sin_easing_out(x0: float, x1: float, y0: float, y1: float, x: float) -> float:
    return y0 + (y1 - y0) * math.sin((x - x0) / (x1 - x0) * math.pi / 2)

def linear(x0: float, x1: float, y0: float, y1: float, x: float) -> float:
    return y0 + (y1 - y0) * (x - x0) / (x1 - x0)

def interpolate_shape(x0: float, x1: float, y0: float, y1: float, x: float, shape: str) -> float:
    if shape == "io":
        return sin_easing_in_out(x0, x1, y0, y1, x)
    elif shape == "i":
        return sin_easing_in(x0, x1, y0, y1, x)
    elif shape == "o":
        return sin_easing_out(x0, x1, y0, y1, x)
    else:
        return linear(x0, x1, y0, y1, x)
