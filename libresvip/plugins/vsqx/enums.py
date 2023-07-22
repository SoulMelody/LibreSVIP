import enum
from typing import Annotated

from pydantic import Field


class VocaloidLanguage(enum.IntEnum):
    JAPANESE: Annotated[int, Field(title="日本語")] = 0
    ENGLISH: Annotated[int, Field(title="English")] = 1
    KOREAN: Annotated[int, Field(title="한국어")] = 2
    SPANISH: Annotated[int, Field(title="Español")] = 3
    SIMPLIFIED_CHINESE: Annotated[int, Field(title="简体中文")] = 4


class VocaloidNoteStyleTypes(enum.Enum):
    ACCENT = "accent"
    BEND_DEP = "bendDep"
    BEND_LEN = "bendLen"
    DECAY = "decay"
    FALL_PORT = "fallPort"
    OPENING = "opening"
    RISE_PORT = "risePort"
    VIBRATO_LENGTH = "vibLen"
    VIBRATO_TYPE = "vibType"
    VIBRATO_DEPTH = "vibDepth"
    VIBRATO_RATE = "vibRate"
