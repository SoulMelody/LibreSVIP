from types import SimpleNamespace
from typing import Final

TICK_RATE: Final[int] = 1470000
DEFAULT_PITCH_TRANSITION: Final[float] = 0.0
DEFAULT_PITCH_PORTAMENTO: Final[float] = 0.07
DEFAULT_PITCH_DEPTH: Final[float] = 0.15
DEFAULT_VIBRATO_START: Final[float] = 0.25
DEFAULT_VIBRATO_FADE: Final[float] = 0.2
DEFAULT_VIBRATO_DEPTH: Final[float] = 1.0
DEFAULT_VIBRATO_FREQUENCY: Final[float] = 5.5
DEFAULT_VIBRATO_PHASE: Final[float] = 0.0
DEFAULT_VIBRATO_JITTER: Final[float] = 1.0
SYSTEM_PITCH_PORTAMENTO: Final[float] = 0.1
SYSTEM_PITCH_DEPTH: Final[float] = 0.0
MAX_BREAK: Final[float] = 0.01
DEFAULT_PHONE_RATIO: Final[float] = 1.8
DEFAULT_DURATIONS = SimpleNamespace(
    stop=0.10,
    affricate=0.125,
    fricative=0.125,
    aspirate=0.094,
    liquid=0.062,
    nasal=0.094,
    vowel=0.0,
    semivowel=0.055,
    diphthong=0.0,
)
