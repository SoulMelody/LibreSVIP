import enum
from typing import Annotated

from pydantic import Field


class VsqxVersion(enum.IntEnum):
    VSQ3: Annotated[int, Field(title="VSQx 3")] = 3
    VSQ4: Annotated[int, Field(title="VSQx 4")] = 4


class VocaloidLanguage(enum.IntEnum):
    JAPANESE: Annotated[int, Field(title="日本語")] = 0
    ENGLISH: Annotated[int, Field(title="English")] = 1
    KOREAN: Annotated[int, Field(title="한국어")] = 2
    SPANISH: Annotated[int, Field(title="Español")] = 3
    SIMPLIFIED_CHINESE: Annotated[int, Field(title="简体中文")] = 4
