from __future__ import annotations

from libresvip.utils.binary.midi import cc11_to_db_change

# MusicXML dynamic markings to MIDI velocity (matches MuseScore 4 defaults).
# Routed through cc11_to_db_change so values use the same scale as
# Track.edited_params.volume produced by the MIDI plugin.
DYNAMIC_TO_VELOCITY: dict[str, int] = {
    "ffffff": 127,
    "fffff": 126,
    "ffff": 124,
    "fff": 120,
    "ff": 112,
    "f": 96,
    "mf": 80,
    "mp": 64,
    "n": 64,
    "p": 49,
    "pp": 36,
    "ppp": 24,
    "pppp": 16,
    "ppppp": 12,
    "pppppp": 8,
    "sf": 112,
    "sfz": 112,
    "sffz": 120,
    "fz": 112,
    "rf": 96,
    "rfz": 96,
    "fp": 96,
    "pf": 80,
    "sfp": 112,
    "sfpp": 112,
    "sfzp": 112,
}


def dynamics_label(tag: str) -> bool:
    return tag in DYNAMIC_TO_VELOCITY


def dyn_label_to_volume(label: str) -> int:
    return round(cc11_to_db_change(DYNAMIC_TO_VELOCITY.get(label, 64)))
