import math


class MusicMath:
    base_freq = 440.0
    a4_midi = 69

    @staticmethod
    def sin_easing_in_out(x0: float, x1: float, y0: float, y1: float, x: float) -> float:
        return y0 + (y1 - y0) * (1 - math.cos((x - x0) / (x1 - x0) * math.pi)) / 2

    @staticmethod
    def sin_easing_in(x0: float, x1: float, y0: float, y1: float, x: float) -> float:
        return y0 + (y1 - y0) * (1 - math.cos((x - x0) / (x1 - x0) * math.pi / 2))

    @staticmethod
    def sin_easing_out(x0: float, x1: float, y0: float, y1: float, x: float) -> float:
        return y0 + (y1 - y0) * math.sin((x - x0) / (x1 - x0) * math.pi / 2)

    @staticmethod
    def linear(x0: float, x1: float, y0: float, y1: float, x: float) -> float:
        return y0 + (y1 - y0) * (x - x0) / (x1 - x0)

    @classmethod
    def interpolate_shape(cls, x0: float, x1: float, y0: float, y1: float, x: float, shape: str) -> float:
        if shape == "io":
            return cls.sin_easing_in_out(x0, x1, y0, y1, x)
        elif shape == "i":
            return cls.sin_easing_in(x0, x1, y0, y1, x)
        elif shape == "o":
            return cls.sin_easing_out(x0, x1, y0, y1, x)
        else:
            return cls.linear(x0, x1, y0, y1, x)
