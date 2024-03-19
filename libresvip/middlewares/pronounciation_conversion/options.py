from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field


class PronounciationConversionOptions(Enum):
    NONE: Annotated[str, Field(title="None")] = "Do nothing"
    HANZI2PINYIN: Annotated[str, Field(title="Hanzi to Pinyin")] = "Hanzi->Pinyin"
    TO_ROMAJI: Annotated[str, Field(title="To Romaji")] = "->Romaji"
    TO_HIRAGANA: Annotated[str, Field(title="To Hiragana")] = "->Hiragana"
    TO_KATAKANA: Annotated[str, Field(title="To Katakana")] = "->Katakana"


class ProcessOptions(BaseModel):
    mode: PronounciationConversionOptions = Field(
        default=PronounciationConversionOptions.NONE,
        title="Pronounciation conversion mode",
        description="Convert lyrics to the specified pronounciation format",
    )
