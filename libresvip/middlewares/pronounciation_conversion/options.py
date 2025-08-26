from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field, create_model

from libresvip.utils.translation import gettext_lazy as _


class PronounciationConversionOptions(Enum):
    _value_: Annotated[
        str,
        create_model(
            "PronounciationConversionOptions",
            __module__="libresvip.middlewares.pronounciation_conversion.options",
            NONE=(str, Field(title=_("None"))),
            HANZI2PINYIN=(str, Field(title=_("Hanzi to Pinyin"))),
            HANZI2JYUTPING=(str, Field(title=_("Hanzi to Jyutping"))),
            HANGUL2ROMANIZATION=(str, Field(title=_("Hangul to Romanization"))),
            KANA2ROMAJI=(str, Field(title=_("Kana to Romaji"))),
            TO_HIRAGANA=(str, Field(title=_("To Hiragana"))),
            TO_KATAKANA=(str, Field(title=_("To Katakana"))),
        ),
    ]
    NONE = "Do nothing"
    HANZI2PINYIN = "Hanzi->Pinyin"
    HANZI2JYUTPING = "Hanzi->Jyutping"
    HANGUL2ROMANIZATION = "Hangul->Romanization"
    KANA2ROMAJI = "Kana->Romaji"
    TO_HIRAGANA = "->Hiragana"
    TO_KATAKANA = "->Katakana"


class ProcessOptions(BaseModel):
    mode: PronounciationConversionOptions = Field(
        default=PronounciationConversionOptions.NONE,
        title=_("Pronounciation conversion mode"),
        description=_("Convert lyrics to the specified pronounciation format"),
    )
