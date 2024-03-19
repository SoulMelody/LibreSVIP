import math
import re
from typing import Optional

from libresvip.core.constants import KEY_IN_OCTAVE


def midi2note(midi: float) -> str:
    pitch_map = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    midi = int(round(midi))
    octave = (midi // KEY_IN_OCTAVE) - 1
    pitch = pitch_map[midi % KEY_IN_OCTAVE]
    return f"{pitch}{octave}"


def note2midi(note: str) -> Optional[int]:
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
        return None

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


def linear_interpolation(x: float, start: tuple[float, float], end: tuple[float, float]) -> float:
    x0, y0 = start
    x1, y1 = end
    return y0 + (x - x0) * (y1 - y0) / (x1 - x0)


def cosine_easing_in_interpolation(
    x: float, start: tuple[float, float], end: tuple[float, float]
) -> float:
    x0, y0 = start
    x1, y1 = end
    return y1 + (y0 - y1) * math.cos((x - x0) / (x1 - x0) * math.pi / 2)


def cosine_easing_out_interpolation(
    x: float, start: tuple[float, float], end: tuple[float, float]
) -> float:
    x0, y0 = start
    x1, y1 = end
    return y0 + (y0 - y1) * math.cos((x - x0) / (x1 - x0) * math.pi / 2 + math.pi / 2)


def cosine_easing_in_out_interpolation(
    x: float, start: tuple[float, float], end: tuple[float, float]
) -> float:
    x0, y0 = start
    x1, y1 = end
    return (y0 + y1) / 2 + (y0 - y1) * math.cos((x - x0) / (x1 - x0) * math.pi) / 2


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

    if using_amplitude:
        return 20 * math.log(ratio, 10)
    else:  # using power
        return 10 * math.log(ratio, 10)
