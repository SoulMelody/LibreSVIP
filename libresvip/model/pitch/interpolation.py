import enum
from collections.abc import Callable

from libresvip.model.point import Point
from libresvip.utils.music_math import (
    interpolate_cosine_ease_in,
    interpolate_cosine_ease_in_out,
    interpolate_cosine_ease_out,
    interpolate_linear,
)

Samples = Callable[[list[Point], int], list[Point]]


class CurveShape(enum.Enum):
    """The easing a curve segment is drawn with.

    An engine's own vocabulary (UTAU's `s`/`j`/`r` bend modes, USTX's
    `lo`/`i`/`o`/`io`/`sp` strings) is mapped onto these members by the plugin
    that owns it, so this enum never has to grow when a new engine appears.
    """

    LINEAR = "linear"
    EASE_IN = "ease_in"
    EASE_OUT = "ease_out"
    EASE_IN_OUT = "ease_in_out"


SHAPE_SAMPLERS: dict[CurveShape, Samples] = {
    CurveShape.LINEAR: interpolate_linear,
    CurveShape.EASE_IN: interpolate_cosine_ease_in,
    CurveShape.EASE_OUT: interpolate_cosine_ease_out,
    CurveShape.EASE_IN_OUT: interpolate_cosine_ease_in_out,
}


def interpolate(
    last_point: Point,
    this_point: Point,
    shape: CurveShape,
    sampling_interval_tick: int,
) -> list[Point]:
    """The segment between two anchors, sampled every `sampling_interval_tick`.

    Both anchors are always included; an interval that does not divide the
    segment simply leaves a longer final step.
    """
    return SHAPE_SAMPLERS[shape]([last_point, this_point], sampling_interval_tick)
