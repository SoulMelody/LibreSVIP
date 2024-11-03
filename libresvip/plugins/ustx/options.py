from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field

from libresvip.model.option_mixins import (
    EnableInstrumentalTrackImportationMixin,
    EnablePitchImportationMixin,
)
from libresvip.utils.translation import gettext_lazy as _


class OpenUtauEnglishPhonemizerCompatibility(Enum):
    NON_ARPA: Annotated[
        str,
        Field(
            title=_("Incompatible with ARPAsing-series Phonemizers"),
        ),
    ] = "non-arpa"
    ARPA: Annotated[
        str,
        Field(
            title=_("Compatible with ARPAsing-series Phonemizers"),
        ),
    ] = "arpa"


class InputOptions(
    EnableInstrumentalTrackImportationMixin,
    EnablePitchImportationMixin,
    BaseModel,
):
    english_phonemizer_compatibility: OpenUtauEnglishPhonemizerCompatibility = Field(
        OpenUtauEnglishPhonemizerCompatibility.NON_ARPA,
        title=_("The way to handle english multisyllabic words"),
        description=_("Compatibility with ARPAsing-series Phonemizer"),
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
