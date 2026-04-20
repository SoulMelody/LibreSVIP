from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field, create_model

from libresvip.model.option_mixins import (
    EnableInstrumentalTrackImportationMixin,
    EnablePitchImportationMixin,
)
from libresvip.utils.translation import gettext_lazy as _


class PlusHandlingMode(Enum):
    _value_: Annotated[
        str,
        create_model(
            "PlusHandlingMode",
            __module__="libresvip.plugins.ustx.options",
            AUTO=(str, Field(title=_("Auto determine by phonemizer language"))),
            MONOSYLLABIC=(
                str,
                Field(title=_("Monosyllabic languages: treating +, +~ and +* as slur notes")),
            ),
            POLYSYLLABIC=(
                str,
                Field(
                    title=_(
                        "Polysyllabic languages: treating + as slur notes, and treating +~ or +* as syllable placerholders"
                    )
                ),
            ),
        ),
    ]
    AUTO = "auto"
    MONOSYLLABIC = "monosyllabic"
    POLYSYLLABIC = "polysyllabic"


class OpenUtauEnglishPhonemizerCompatibility(Enum):
    _value_: Annotated[
        str,
        create_model(
            "OpenUtauEnglishPhonemizerCompatibility",
            __module__="libresvip.plugins.ustx.options",
            NON_ARPA=(str, Field(title=_("Incompatible with ARPAsing-series Phonemizers"))),
            ARPA=(str, Field(title=_("Compatible with ARPAsing-series Phonemizers"))),
        ),
    ]
    NON_ARPA = "non-arpa"
    ARPA = "arpa"


class InputOptions(
    EnableInstrumentalTrackImportationMixin,
    EnablePitchImportationMixin,
    BaseModel,
):
    plus_handling_mode: PlusHandlingMode = Field(
        PlusHandlingMode.AUTO,
        title=_("Plus sign handling mode"),
        description=_("How to handle the + symbol in lyrics when importing USTX"),
    )
    breath_lyrics: str = Field(
        "Asp AP",
        title=_("Breath lyrics"),
        description=_(
            "Special lyrics that will be recognized as breath notes only when immediately followed by a regular note, each separated by a space"
        ),
    )
    silence_lyrics: str = Field(
        "R SP",
        title=_("Silence lyrics"),
        description=_("Special lyrics that will be ignored, each separated by a space"),
    )


class OutputOptions(BaseModel):
    english_phonemizer_compatibility: OpenUtauEnglishPhonemizerCompatibility = Field(
        OpenUtauEnglishPhonemizerCompatibility.NON_ARPA,
        title=_("The way to handle english multisyllabic words"),
        description=_("Compatibility with ARPAsing-series Phonemizer"),
    )
