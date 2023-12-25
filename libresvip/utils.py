import contextlib
import contextvars
import gettext
import io
import math
import pathlib
import re
import textwrap
from numbers import Real
from typing import Callable, Optional, TypeVar, Union, cast
from xml.sax import saxutils

import charset_normalizer
import zhon
from more_itertools import locate, rlocate
from pymediainfo import ET, MediaInfo
from pymediainfo import Track as MediaInfoTrack

from libresvip.core.constants import KEY_IN_OCTAVE

T = TypeVar("T")
lazy_translation: contextvars.ContextVar[
    Optional[gettext.NullTranslations]
] = contextvars.ContextVar("translator")


SYMBOL_PATTERN = re.compile(
    rf"(?!-)[\!\"\#\$%\&'\(\)\*,\./:;<=>\?\[\\\]\^_`\{{\|\}}\~{zhon.hanzi.punctuation}]+"
)


def to_unicode(content: bytes) -> str:
    guessed_charset = charset_normalizer.detect(content)
    encoding = (
        "utf-8"
        if guessed_charset["encoding"] is None
        else cast(str, guessed_charset["encoding"])
    )
    return content.decode(encoding)


def find_index(obj_list: list[T], pred: Callable[[T], bool]) -> int:
    return next(locate(obj_list, pred), -1)


def find_last_index(obj_list: list[T], pred: Callable[[T], bool]) -> int:
    return next(rlocate(obj_list, pred), -1)


def binary_find_first(n: list[T], pred: Callable[[T], bool]) -> Optional[T]:
    if not len(n):
        return None
    left, right = 0, len(n) - 1
    while right > left:
        middle = (left + right) // 2
        if pred(n[middle]):
            right = middle
        else:
            left = middle + 1
    return n[right] if pred(n[right]) else None


def binary_find_last(n: list[T], pred: Callable[[T], bool]) -> Optional[T]:
    if not len(n):
        return None
    left, right = 0, len(n) - 1
    while right > left:
        middle = (left + right + 1) // 2
        if pred(n[middle]):
            left = middle
        else:
            right = middle - 1
    return n[left] if pred(n[left]) else None


def gettext_lazy(message: str) -> str:
    with contextlib.suppress(LookupError):
        if (translation := lazy_translation.get()) is not None:
            return translation.gettext(message)
    try:
        return _(message)
    except NameError:
        return message


def shorten_error_message(message: Optional[str]) -> str:
    if message is None:
        return ""
    error_lines = textwrap.wrap(message, 70)
    if len(error_lines) > 30:
        message = "\n".join(error_lines[:15] + ["..."] + error_lines[-15:])
    else:
        message = "\n".join(error_lines)
    return message


def clamp(
    x: Real,
    lower: Real = cast(Real, float("-inf")),
    upper: Real = cast(Real, float("inf")),
) -> Real:
    """Limit a value to a given range.

    The returned value is guaranteed to be between *lower* and
    *upper*. Integers, floats, and other comparable types can be
    mixed.

    Similar to `numpy's clip`_ function.

    .. _numpy's clip: http://docs.scipy.org/doc/numpy/reference/generated/numpy.clip.html
    .. from boltons: https://boltons.readthedocs.io/en/latest/mathutils.html#boltons.mathutils.clamp

    """
    if upper < lower:
        raise ValueError(
            "expected upper bound (%r) >= lower bound (%r)" % (upper, lower),
        )
    return min(max(x, lower), upper)


def audio_track_info(
    file_path: Union[str, pathlib.Path], only_wav: bool = False
) -> Optional[MediaInfoTrack]:
    def filter_func(track: MediaInfoTrack) -> bool:
        return track.format == "PCM" if only_wav else (track.duration is not None)

    if MediaInfo.can_parse():
        with contextlib.suppress(
            FileNotFoundError, ET.ParseError, RuntimeError, ValueError
        ):
            media_info = MediaInfo.parse(file_path)
            if not len(media_info.video_tracks):
                return next(
                    (track for track in media_info.audio_tracks if filter_func(track)),
                    None,
                )
    return None


# convertion functions adapted from librosa and pydub
def midi2hz(midi: float, a4_midi: int = 69, base_freq: float = 440.0) -> float:
    return base_freq * 2 ** ((midi - a4_midi) / KEY_IN_OCTAVE)


def hz2midi(hz: float, a4_midi: int = 69, base_freq: float = 440.0) -> float:
    return a4_midi + KEY_IN_OCTAVE * math.log2(hz / base_freq)


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


def midi2note(midi: float) -> str:
    pitch_map = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    midi = int(round(midi))
    octave = (midi // KEY_IN_OCTAVE) - 1
    pitch = pitch_map[midi % KEY_IN_OCTAVE]
    return f"{pitch}{octave}"


# convertion functions copied from pydub
def db_to_float(db: float, using_amplitude: bool = True) -> float:
    """
    Converts the input db to a float, which represents the equivalent
    ratio in power.
    """
    return 10 ** (db / 20) if using_amplitude else 10 ** (db / 10)


def ratio_to_db(
    ratio: float, val2: Optional[float] = None, using_amplitude: bool = True
) -> float:
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


class EchoGenerator(saxutils.XMLGenerator):
    # from https://code.activestate.com/recipes/84516-using-the-sax2-lexicalhandler-interface/

    def __init__(
        self,
        out: Optional[io.IOBase] = None,
        encoding: str = "iso-8859-1",
        short_empty_elements: bool = False,
    ) -> None:
        super().__init__(out, encoding, short_empty_elements)
        self._in_entity = 0
        self._in_cdata = 0
        self._write: Callable[[str], None]

    def characters(self, content: str) -> None:
        if self._in_entity:
            return
        elif self._in_cdata:
            self._write(content)
        else:
            super().characters(content)

    # -- LexicalHandler interface

    def comment(self, content: str) -> None:
        self._write(f"<!--{content!r}-->")

    def start_dtd(self, name: str, public_id: str, system_id: str) -> None:
        self._write(f"<!DOCTYPE {name}")
        if public_id:
            self._write(
                f" PUBLIC {saxutils.quoteattr(public_id)} {saxutils.quoteattr(system_id)}",
            )
        elif system_id:
            self._write(f" SYSTEM {saxutils.quoteattr(system_id)}")

    def end_dtd(self) -> None:
        self._write(">\n")

    def start_entity(self, name: str) -> None:
        self._write(f"&{name};")
        self._in_entity = 1

    def end_entity(self, name: str) -> None:
        self._in_entity = 0

    def start_cdata(self) -> None:
        self._write("<![CDATA[")
        self._in_cdata = 1

    def end_cdata(self) -> None:
        self._write("]]>")
        self._in_cdata = 0
