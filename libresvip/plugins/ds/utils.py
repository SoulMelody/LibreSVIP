import math

import regex as re


def midi2hz(midi: float, a4_midi=69, base_freq=440.0) -> float:
    return base_freq * 2 ** ((midi - a4_midi) / 12)


def hz2midi(hz: float, a4_midi=69, base_freq=440.0) -> float:
    return a4_midi + 12 * math.log2(hz / base_freq)


def note2midi(note, *, round_midi=True):
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
