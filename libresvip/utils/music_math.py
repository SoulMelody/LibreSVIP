import functools
import math
import re
from collections.abc import Callable
from typing import Optional

from more_itertools import pairwise
from typing_extensions import Concatenate, ParamSpec

from libresvip.core.constants import KEY_IN_OCTAVE
from libresvip.model.point import Point

P = ParamSpec("P")


def midi2note(midi: float) -> str:
    pitch_map = [
        "C",
        "C#",
        "D",
        "D#",
        "E",
        "F",
        "F#",
        "G",
        "G#",
        "A",
        "A#",
        "B",
    ]
    midi = int(round(midi))
    octave = (midi // KEY_IN_OCTAVE) - 1
    pitch = pitch_map[midi % KEY_IN_OCTAVE]
    return f"{pitch}{octave}"


def note2midi(note: str) -> int:
    pitch_map = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
    acc_map = {
        "#": 1,
        "": 0,
        "b": -1,
        "!": -1,
        "♯": 1,
        "𝄪": 2,
        "♭": -1,
        "𝄫": -2,
        "♮": 0,
    }

    match = re.match(
        r"^(?P<note>[A-Ga-g])" r"(?P<accidental>[#♯𝄪b!♭𝄫♮]*)" r"(?P<octave>[+-]?\d+)?$",
        note,
    )
    if not match:
        msg = f"Invalid note format: {note!r}"
        raise ValueError(msg)

    pitch = match["note"].upper()
    offset = sum(acc_map[o] for o in match["accidental"])
    octave = match["octave"]

    octave = int(octave) if octave else 0

    note_value = KEY_IN_OCTAVE * (octave + 1) + pitch_map[pitch] + offset

    return int(round(note_value))


def hz2midi(hz: float, a4_midi: int = 69, base_freq: float = 440.0) -> float:
    return a4_midi + KEY_IN_OCTAVE * math.log2(hz / base_freq)


def midi2hz(midi: float, a4_midi: int = 69, base_freq: float = 440.0) -> float:
    return base_freq * 2 ** ((midi - a4_midi) / KEY_IN_OCTAVE)


def clamp(
    x: float,
    lower: float = float("-inf"),
    upper: float = float("inf"),
) -> float:
    """Limit a value to a given range.

    The returned value is guaranteed to be between *lower* and
    *upper*. Integers, floats, and other comparable types can be
    mixed.

    Similar to `numpy's clip`_ function.

    .. _numpy's clip: http://docs.scipy.org/doc/numpy/reference/generated/numpy.clip.html
    .. from boltons: https://boltons.readthedocs.io/en/latest/mathutils.html#boltons.mathutils.clamp

    """
    if upper < lower:
        msg = f"expected upper bound ({upper!r}) >= lower bound ({lower!r})"
        raise ValueError(msg)
    return min(max(x, lower), upper)


def _transform_interpolation_args(
    func: Callable[Concatenate[float, P], float],
) -> Callable[[float, tuple[float, float], tuple[float, float]], float]:
    @functools.wraps(func, assigned=["__module__", "__name__", "__qualname__", "__doc__"])
    def inner(
        x: float,
        start: tuple[float, float],
        end: tuple[float, float],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> float:
        x0, y0 = start
        x1, y1 = end
        r = (x - x0) / (x1 - x0)
        return y0 + (y1 - y0) * func(r, *args, **kwargs)

    return inner


@_transform_interpolation_args
def linear_interpolation(r: float) -> float:
    return r


@_transform_interpolation_args
def cosine_easing_in_interpolation(r: float) -> float:
    return 1 - math.cos(r * math.pi / 2)


@_transform_interpolation_args
def cosine_easing_out_interpolation(r: float) -> float:
    return math.sin(r * math.pi / 2)


@_transform_interpolation_args
def cosine_easing_in_out_interpolation(r: float) -> float:
    return (1 - math.cos(r * math.pi)) / 2


@_transform_interpolation_args
def cubic_interpolation(r: float) -> float:
    return (3 - 2 * r) * r**2


@_transform_interpolation_args
def vocaloid_interpolation(r: float) -> float:
    return math.sin(r * math.pi) / 2 if r <= 0.5 else r


@_transform_interpolation_args
def sigmoid_interpolation(r: float, k: float) -> float:
    return 1 / (1 + math.exp(k * (-2 * r + 1)))


def _inner_interpolate(
    data: list[Point],
    sampling_interval_tick: int,
    mapping: Callable[[int, Point, Point], float],
) -> list[Point]:
    return (
        (
            [data[0]]
            + [
                Point(x=x, y=round(mapping(x, start, end)))
                for start, end in pairwise(data)
                for x in range(start.x + 1, end.x, sampling_interval_tick)
            ]
            + [data[-1]]
        )
        if data
        else data
    )


interpolate_linear = functools.partial(_inner_interpolate, mapping=linear_interpolation)
interpolate_cosine_ease_in_out = functools.partial(
    _inner_interpolate, mapping=cosine_easing_in_out_interpolation
)
interpolate_cosine_ease_in = functools.partial(
    _inner_interpolate, mapping=cosine_easing_in_interpolation
)
interpolate_cosine_ease_out = functools.partial(
    _inner_interpolate, mapping=cosine_easing_out_interpolation
)


def db_to_float(db: float, using_amplitude: bool = True) -> float:
    """
    Converts the input db to a float, which represents the equivalent
    ratio in power.
    """
    return 10 ** (db / 20) if using_amplitude else 10 ** (db / 10)


def ratio_to_db(ratio: float, val2: Optional[float] = None, using_amplitude: bool = True) -> float:
    """
    Converts the input float to db, which represents the equivalent
    to the ratio in power represented by the multiplier passed in.
    """

    # accept 2 values and use the ratio of val1 to val2
    if val2 is not None:
        ratio /= val2

    # special case for multiply-by-zero (convert to silence)
    if ratio == 0:
        return -float("inf")

    return 20 * math.log10(ratio) if using_amplitude else 10 * math.log10(ratio)
