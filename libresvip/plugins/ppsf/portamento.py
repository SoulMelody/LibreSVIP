from collections.abc import Callable

from libresvip.utils.music_math import (
    cosine_easing_in_out_interpolation,
    linear_interpolation,
    quadratic_easing_in_out_interpolation,
)

PORTAMENTO_LINEAR = 0
PORTAMENTO_CUBIC = 1
PORTAMENTO_TRANSIENT = 2
PORTAMENTO_SINE = 3
PORTAMENTO_FREE = 4
PORTAMENTO_DEFAULT = 5
PORTAMENTO_CUBIC_ORNAMENT_2A = 6
PORTAMENTO_CUBIC_ORNAMENT_2B = 7

EMITTED_PORTAMENTO_TYPE = PORTAMENTO_CUBIC


def glide_interpolation(portamento_type: int) -> Callable[..., float]:
    """Return the base-pitch interpolation used for ``portamento_type``."""
    if portamento_type == PORTAMENTO_LINEAR:
        return linear_interpolation
    if portamento_type == PORTAMENTO_SINE:
        return cosine_easing_in_out_interpolation
    return quadratic_easing_in_out_interpolation


GLIDE_INTERPOLATION = glide_interpolation(EMITTED_PORTAMENTO_TYPE)


def portamento_span(pos: int, offset: int, length: int) -> tuple[int, int]:
    """Return the ``[start, end)`` tick span of the glide into ``pos``."""
    return pos + offset, pos + offset + length
