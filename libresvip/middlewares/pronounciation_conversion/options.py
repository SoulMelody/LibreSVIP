from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field

from libresvip.utils.translation import gettext_lazy as _


class PronounciationConversionOptions(Enum):
    NONE: Annotated[str, Field(title=_("None"))] = "Do nothing"
    HANZI2PINYIN: Annotated[str, Field(title=_("Hanzi to Pinyin"))] = "Hanzi->Pinyin"
    TO_ROMAJI: Annotated[str, Field(title=_("To Romaji"))] = "->Romaji"
    TO_HIRAGANA: Annotated[str, Field(title=_("To Hiragana"))] = "->Hiragana"
    TO_KATAKANA: Annotated[str, Field(title=_("To Katakana"))] = "->Katakana"


class ProcessOptions(BaseModel):
    mode: PronounciationConversionOptions = Field(
        default=PronounciationConversionOptions.NONE,
        title=_("Pronounciation conversion mode"),
        description=_("Convert lyrics to the specified pronounciation format"),
    )
