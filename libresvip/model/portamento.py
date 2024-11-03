from __future__ import annotations

from dataclasses import dataclass
from functools import partial
from typing import TYPE_CHECKING

from libresvip.utils.music_math import (
    cosine_easing_in_out_interpolation,
    cubic_interpolation,
    linear_interpolation,
    sigmoid_interpolation,
    vocaloid_interpolation,
)

if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass
class PortamentoPitch:
    max_inter_time_in_secs: float
    max_inter_time_percent: float
    inter_func: Callable[[float, tuple[float, float], tuple[float, float]], float]
    vocaloid_mode: bool = False

    @classmethod
    def no_portamento(cls) -> PortamentoPitch:
        return cls(0.0, 0.0, linear_interpolation)

    @classmethod
    def cosine_portamento(cls) -> PortamentoPitch:
        return cls(0.05, 0.1, cosine_easing_in_out_interpolation)

    @classmethod
    def cubic_portamento(cls) -> PortamentoPitch:
        return cls(0.05, 0.1, cubic_interpolation)

    @classmethod
    def sigmoid_portamento(cls) -> PortamentoPitch:
        return cls(0.075, 0.48, partial(sigmoid_interpolation, k=5.5))  # type: ignore[call-arg]

    @classmethod
    def vocaloid_portamento(cls) -> PortamentoPitch:
        return cls(0.05, 0.15, vocaloid_interpolation, True)
