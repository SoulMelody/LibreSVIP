from enum import Enum, IntEnum
from typing import Annotated, NamedTuple

from pydantic import BaseModel, Field, create_model

from libresvip.model.option_mixins import (
    EnableBreathImportationMixin,
    EnableGenderImportationMixin,
    EnableInstrumentalTrackImportationMixin,
    EnablePitchImportationMixin,
    EnableStrengthImportationMixin,
    EnableVolumeImportationMixin,
)
from libresvip.utils.translation import gettext_lazy as _


class SynthVLanguagePreset(NamedTuple):
    language: str
    phoneset: str


synthv_language_presets = {
    "mandarin": SynthVLanguagePreset(language="mandarin", phoneset="xsampa"),
    "cantonese": SynthVLanguagePreset(language="cantonese", phoneset="xsampa"),
    "japanese": SynthVLanguagePreset(language="japanese", phoneset="romaji"),
    "english": SynthVLanguagePreset(language="english", phoneset="arpabet"),
    "spanish": SynthVLanguagePreset(language="spanish", phoneset="xsampa"),
    "korean": SynthVLanguagePreset(language="korean", phoneset="xsampa"),
}


class SVProjectVersionCompatibility(IntEnum):
    _value_: Annotated[
        int,
        create_model(
            "SVProjectVersionCompatibility",
            __module__="libresvip.plugins.svp.options",
            BELOW_1_9_0=(
                int,
                Field(title=_("Compatible with Synthesizer V Studio 1.9.0 and below")),
            ),
            BETWEEN_1_10_0_AND_1_11_2=(
                int,
                Field(title=_("Compatible with Synthesizer V Studio 1.10.0 to 1.11.2")),
            ),
            ABOVE_2_0_0=(int, Field(title=_("Compatible with Synthesizer V Studio 2.0 and up"))),
        ),
    ]
    BELOW_1_9_0 = 100
    BETWEEN_1_10_0_AND_1_11_2 = 135
    ABOVE_2_0_0 = 182


class LanguageOption(Enum):
    _value_: Annotated[
        str,
        create_model(
            "LanguageOption",
            __module__="libresvip.plugins.svp.options",
            MANDARIN=(str, Field(title=_("Mandarin"))),
            CANTONESE=(str, Field(title=_("Cantonese"))),
            JAPANESE=(str, Field(title=_("Japanese"))),
            ENGLISH=(str, Field(title=_("English"))),
            SPANISH=(str, Field(title=_("Spanish"))),
            KOREAN=(str, Field(title=_("Korean"))),
        ),
    ]
    MANDARIN = "mandarin"
    CANTONESE = "cantonese"
    JAPANESE = "japanese"
    ENGLISH = "english"
    SPANISH = "spanish"
    KOREAN = "korean"


class BreathOption(Enum):
    _value_: Annotated[
        str,
        create_model(
            "BreathOption",
            __module__="libresvip.plugins.svp.options",
            IGNORE=(str, Field(title=_("Ignore all breath notes"))),
            KEEP=(str, Field(title=_("Keep as normal notes"))),
            CONVERT=(str, Field(title=_("Convert to breath mark"))),
        ),
    ]
    IGNORE = "ignore"
    KEEP = "keep"
    CONVERT = "convert"


class GroupOption(Enum):
    _value_: Annotated[
        str,
        create_model(
            "GroupOption",
            __module__="libresvip.plugins.svp.options",
            SPLIT=(
                str,
                Field(
                    title=_("Split all to tracks"),
                    description=_("Generate a track for each note group reference"),
                ),
            ),
            MERGE=(
                str,
                Field(
                    title=_("Keep original position"),
                    description=_("Split note groups to separate tracks only when notes overlap"),
                ),
            ),
        ),
    ]
    SPLIT = "split"
    MERGE = "merge"


class PitchOption(Enum):
    _value_: Annotated[
        str,
        create_model(
            "PitchOption",
            __module__="libresvip.plugins.svp.options",
            FULL=(
                str,
                Field(
                    title=_("Full pitch curve"),
                    description=_("Input the full pitch curve regardless of editing"),
                ),
            ),
            VIBRATO=(
                str,
                Field(
                    title=_("Edited part only (vibrato mode)"),
                    description=_(
                        "Input the edited part of pitch curve; default vibrato will be imported if not edited"
                    ),
                ),
            ),
            PLAIN=(
                str,
                Field(
                    title=_("Edited part only (plain mode)"),
                    description=_(
                        "Input the edited part of pitch curve; default vibrato will be ignored"
                    ),
                ),
            ),
        ),
    ]
    FULL = "full"
    VIBRATO = "vibrato"
    PLAIN = "plain"


class VibratoOption(Enum):
    _value_: Annotated[
        str,
        create_model(
            "VibratoOption",
            __module__="libresvip.plugins.svp.options",
            NONE=(
                str,
                Field(
                    title=_("All removed"),
                    description=_(
                        "All notes will be set to 0 vibrato depth to ensure the output pitch curve is the same as input"
                    ),
                ),
            ),
            ALWAYS=(
                str,
                Field(
                    title=_("All kept"),
                    description=_(
                        "Keep all notes' default vibrato, but may cause inconsistent pitch curves"
                    ),
                ),
            ),
            HYBRID=(
                str,
                Field(
                    title=_("Hybrid mode"),
                    description=_(
                        "Remove vibrato in edited part, keep default vibrato in other parts"
                    ),
                ),
            ),
        ),
    ]
    NONE = "none"
    ALWAYS = "always"
    HYBRID = "hybrid"


class InputOptions(
    EnableBreathImportationMixin,
    EnableGenderImportationMixin,
    EnableInstrumentalTrackImportationMixin,
    EnablePitchImportationMixin,
    EnableStrengthImportationMixin,
    EnableVolumeImportationMixin,
    BaseModel,
):
    instant: bool = Field(
        default=True,
        title=_("Always follow instant pitch mode"),
        description=_(
            "When this option is turned off, the default pitch curve will always be imported regardless of the project setting. If you have tuned the pitch curve based on instant pitch mode, it is recommended to turn on this option."
        ),
    )
    pitch: PitchOption = Field(
        default=PitchOption.PLAIN,
        title=_("Pitch input mode"),
        description=_(
            'This option controls the range of pitch curve to be imported and the judgment condition. The definition of "edited part" is: the pitch deviation in the parameter panel, the pitch transition in the vibrato envelope and the pitch transition in the note properties have been edited.'
        ),
    )
    breath: BreathOption = Field(
        default=BreathOption.CONVERT,
        title=_("The way to handle breath notes"),
    )
    group: GroupOption = Field(
        default=GroupOption.SPLIT,
        title=_("The way to handle note groups"),
        description=_(
            'Notice: If there are too many note groups, please choose "Keep original position" to avoid excessive track count. But if there are notes that are adjacent (but not overlapped) between note groups or between note groups and main group, it is recommended to choose "Split to tracks" to ensure the paragraph division is not broken.'
        ),
    )


class OutputOptions(BaseModel):
    version_compatibility: SVProjectVersionCompatibility = Field(
        default=SVProjectVersionCompatibility.BELOW_1_9_0,
        title=_("Version compatibility"),
    )
    vibrato: VibratoOption = Field(
        default=VibratoOption.NONE, title=_("The way to handle vibrato notes")
    )
    down_sample: int = Field(
        default=40,
        title=_(
            "Set the average sampling interval of parameter points to improve performance (0 means no limit)"
        ),
        description=_(
            "Reduce the sampling interval to improve the accuracy of parameter curves, but may cause rendering lag (e.g. Synthesizer V Studio Pro + AI voicebank). Please set this value according to your hardware configuration and actual experience."
        ),
    )
    language_override: LanguageOption = Field(
        default=LanguageOption.MANDARIN,
        title=_("Override default language for the voicebank"),
    )
