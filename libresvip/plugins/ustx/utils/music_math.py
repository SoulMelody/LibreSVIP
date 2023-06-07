import enum
import math
from gettext import gettext as _

import regex as re
from pydub.utils import db_to_float, ratio_to_db


class KeyColor(enum.IntEnum):
    WHITE = 0
    BLACK = 1


class MusicMath:
    base_freq = 440.0
    a4_midi = 69

    keys_in_octave: list[tuple[str, KeyColor]] = [
        ("C", KeyColor.WHITE),
        ("C#", KeyColor.BLACK),
        ("D", KeyColor.WHITE),
        ("D#", KeyColor.BLACK),
        ("E", KeyColor.WHITE),
        ("F", KeyColor.WHITE),
        ("F#", KeyColor.BLACK),
        ("G", KeyColor.WHITE),
        ("G#", KeyColor.BLACK),
        ("A", KeyColor.WHITE),
        ("A#", KeyColor.BLACK),
        ("B" , KeyColor.WHITE),
    ]

    zoom_ratios = [4.0, 2.0, 1.0, 1.0 / 2, 1.0 / 4, 1.0 / 8, 1.0 / 16, 1.0 / 32, 1.0 / 64]

    @classmethod
    def get_tone_name(cls, midi: float, *, round_midi=True) -> str:
        pitch_map = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        if round_midi:
            midi = int(round(midi))
        octave = (midi // 12) - 1
        pitch = pitch_map[midi % 12]
        return f"{pitch}{octave}"

    @classmethod
    def name_to_tone(cls, note: str, *, round_midi=True) -> float:
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
            raise ValueError("Improper note format: {:s}".format(note))

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

    @classmethod
    def is_black_key(cls, note_num: int) -> bool:
        return cls.keys_in_octave[note_num % 12][1] == KeyError.black

    @staticmethod
    def is_center_key(note_num: int) -> bool:
        return note_num % 12 == 0

    @classmethod
    def get_zoom_ratio(cls, quarter_width: float, beat_per_bar: int, beat_unit: int, min_width: float) -> float:
        i = 0
        if beat_unit == 2:
            i = 0
        elif beat_unit == 4:
            i = 1
        elif beat_unit == 8:
            i = 2
        elif beat_unit == 16:
            i = 3
        else:
            raise Exception(_("Invalid beat unit."))
        if beat_per_bar % 4 == 0:
            i -= 1
        if quarter_width * beat_per_bar * 4 <= min_width * beat_unit:
            return beat_per_bar / beat_unit * 4
        while i + 1 < len(cls.zoom_ratios) and quarter_width * cls.zoom_ratios[i + 1] > min_width:
            i += 1
        return cls.zoom_ratios[i]

    @staticmethod
    def tick_to_millisecond(tick: float, bpm: float, beat_unit: int, resolution: int) -> float:
        return tick * 60000.0 / bpm * beat_unit / 4 / resolution

    @staticmethod
    def millisecond_to_tick(ms: float, bpm: float, beat_unit: int, resolution: int) -> int:
        return int(ms / 60000.0 * bpm / beat_unit * 4 * resolution + 0.5)

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

    @staticmethod
    def decibel_to_linear(db: float) -> float:
        return db_to_float(db)

    @staticmethod
    def linear_to_decibel(v: float) -> float:
        return ratio_to_db(v)

    @classmethod
    def tone_to_freq(cls, midi: int) -> float:
        return cls.base_freq * 2 ** ((midi - cls.a4_midi) / 12)

    @classmethod
    def freq_to_tone(cls, hz: float) -> float:
        return cls.a4_midi + 12 * math.log2(hz / cls.base_freq)
