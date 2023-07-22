import contextlib
import contextvars
import functools
import gettext
import math
import pathlib
from types import FunctionType
from typing import Callable, Optional, TypeVar
from xml.sax import saxutils

import charset_normalizer
import regex as re
from more_itertools import locate, rlocate

T = TypeVar("T")
lazy_translation: contextvars.ContextVar[
    Optional[gettext.NullTranslations]
] = contextvars.ContextVar("translator")


def ensure_path(func: FunctionType) -> FunctionType:
    @functools.wraps(func)
    def wrapper(self, path, *args, **kwargs):
        if not isinstance(path, pathlib.Path):
            path = pathlib.Path(path)
        return func(self, path, *args, **kwargs)

    return wrapper


def to_unicode(content: bytes) -> str:
    guessed_charset = charset_normalizer.detect(content)
    if guessed_charset["encoding"] is None:
        encoding = "utf-8"
    else:
        encoding = guessed_charset["encoding"]
    return content.decode(encoding)


@ensure_path
def read_file(path: pathlib.Path) -> str:
    content = path.read_bytes()
    return to_unicode(content)


def find_index(obj_list: list[T], pred: Callable[[T], bool]) -> int:
    return next(locate(obj_list, pred), -1)


def find_last_index(obj_list: list[T], pred: Callable[[T], bool]) -> int:
    return next(rlocate(obj_list, pred), -1)


def download_and_setup_ffmpeg():
    with contextlib.suppress(ImportError):
        import static_ffmpeg
        import static_ffmpeg.run

        # static_ffmpeg.run.PLATFORM_ZIP_FILES = {
        #     platform: "https://ghproxy.com/" + url
        #     for platform, url in static_ffmpeg.run.PLATFORM_ZIP_FILES.items()
        # }

        static_ffmpeg.add_paths()


def gettext_lazy(message: str) -> str:
    if (translation := lazy_translation.get()) is not None:
        return translation.gettext(message)
    try:
        return gettext(message)
    except NameError:
        return message


def shorten_error_message(message: Optional[str]) -> str:
    if message is None:
        return ""
    error_lines = message.splitlines()
    if len(error_lines) > 30:
        message = "\n".join(error_lines[:15] + ["..."] + error_lines[-15:])
    return message


def midi2hz(midi: float, a4_midi=69, base_freq=440.0) -> float:
    return base_freq * 2 ** ((midi - a4_midi) / 12)


def hz2midi(hz: float, a4_midi=69, base_freq=440.0) -> float:
    return a4_midi + 12 * math.log2(hz / base_freq)


def note2midi(note: str, *, round_midi=True) -> float:
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
        r"^(?P<note>[A-Ga-g])"
        r"(?P<accidental>[#♯𝄪b!♭𝄫♮]*)"
        r"(?P<octave>[+-]?\d+)?"
        r"(?P<cents>[+-]\d+)?$",
        note,
    )
    if not match:
        return None

    pitch = match.group("note").upper()
    offset = sum(acc_map[o] for o in match.group("accidental"))
    octave = match.group("octave")
    cents = match.group("cents")

    if not octave:
        octave = 0
    else:
        octave = int(octave)

    if not cents:
        cents = 0
    else:
        cents = int(cents) * 1e-2

    note_value = 12 * (octave + 1) + pitch_map[pitch] + offset + cents

    if round_midi:
        note_value = int(round(note_value))

    return note_value


def midi2note(midi: float, *, round_midi=True) -> str:
    pitch_map = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    if round_midi:
        midi = int(round(midi))
    octave = (midi // 12) - 1
    pitch = pitch_map[midi % 12]
    return f"{pitch}{octave}"


class EchoGenerator(saxutils.XMLGenerator):
    # from https://code.activestate.com/recipes/84516-using-the-sax2-lexicalhandler-interface/

    def __init__(self, out=None, encoding="iso-8859-1", short_empty_elements=False):
        super().__init__(out, encoding, short_empty_elements)
        self._in_entity = 0
        self._in_cdata = 0

    def characters(self, content):
        if self._in_entity:
            return
        elif self._in_cdata:
            self._write(content)
        else:
            super().characters(content)

    # -- LexicalHandler interface

    def comment(self, content):
        self._write(f"<!--{content}-->")

    def start_dtd(self, name, public_id, system_id):
        self._write(f"<!DOCTYPE {name}")
        if public_id:
            self._write(
                f" PUBLIC {saxutils.quoteattr(public_id)} {saxutils.quoteattr(system_id)}"
            )
        elif system_id:
            self._write(f" SYSTEM {saxutils.quoteattr(system_id)}")

    def end_dtd(self):
        self._write(">\n")

    def start_entity(self, name):
        self._write(f"&{name};")
        self._in_entity = 1

    def end_entity(self, name):
        self._in_entity = 0

    def start_cdata(self):
        self._write("<![CDATA[")
        self._in_cdata = 1

    def end_cdata(self):
        self._write("]]>")
        self._in_cdata = 0
