import math


def linear_interpolation(x: float) -> float:
    return x


def cubic_interpolation(x: float) -> float:
    return (3 - 2 * x) * x**2


def cosine_interpolation(x: float) -> float:
    return (1 - math.cos(math.pi * x)) / 2


def sigmoid_interpolation(x: float, k: float) -> float:
    return 1 / (1 + math.exp(k * (-2 * x + 1)))
