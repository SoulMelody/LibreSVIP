from enum import Enum, IntEnum
from typing import Annotated, NamedTuple

from pydantic import BaseModel, Field

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
}


class SVProjectVersionCompatibility(IntEnum):
    BELOW_1_9_0: Annotated[
        int,
        Field(title=_("Compatible with SynthesizerV Studio 1.9.0 and below")),
    ] = 100
    ABOVE_1_9_0: Annotated[
        int,
        Field(title=_("Incompatible with SynthesizerV Studio 1.9.0 and below")),
    ] = 135


class LanguageOption(Enum):
    MANDARIN: Annotated[str, Field(title=_("Mandarin"))] = "mandarin"
    CANTONESE: Annotated[str, Field(title=_("Cantonese"))] = "cantonese"
    JAPANESE: Annotated[str, Field(title=_("Japanese"))] = "japanese"
    ENGLISH: Annotated[str, Field(title=_("English"))] = "english"
    SPANISH: Annotated[str, Field(title=_("Spanish"))] = "spanish"


class BreathOption(Enum):
    IGNORE: Annotated[str, Field(title=_("Ignore all breath notes"))] = "ignore"
    KEEP: Annotated[str, Field(title=_("Keep as normal notes"))] = "keep"
    CONVERT: Annotated[str, Field(title=_("Convert to breath mark"))] = "convert"


class GroupOption(Enum):
    SPLIT: Annotated[
        str,
        Field(
            title=_("Split all to tracks"),
            description=_("Generate a track for each note group reference"),
        ),
    ] = "split"
    MERGE: Annotated[
        str,
        Field(
            title=_("Keep original position"),
            description=_("Split note groups to separate tracks only when notes overlap"),
        ),
    ] = "merge"


class PitchOption(Enum):
    FULL: Annotated[
        str,
        Field(
            title=_("Full pitch curve"),
            description=_("Input the full pitch curve regardless of editing"),
        ),
    ] = "full"
    VIBRATO: Annotated[
        str,
        Field(
            title=_("Edited part only (vibrato mode)"),
            description=_(
                "Input the edited part of pitch curve; default vibrato will be imported if not edited"
            ),
        ),
    ] = "vibrato"
    PLAIN: Annotated[
        str,
        Field(
            title=_("Edited part only (plain mode)"),
            description=_("Input the edited part of pitch curve; default vibrato will be ignored"),
        ),
    ] = "plain"


class VibratoOption(Enum):
    NONE: Annotated[
        str,
        Field(
            title=_("All removed"),
            description=_(
                "All notes will be set to 0 vibrato depth to ensure the output pitch curve is the same as input"
            ),
        ),
    ] = "none"
    ALWAYS: Annotated[
        str,
        Field(
            title=_("All kept"),
            description=_(
                "Keep all notes' default vibrato, but may cause inconsistent pitch curves"
            ),
        ),
    ] = "always"
    HYBRID: Annotated[
        str,
        Field(
            title=_("Hybrid mode"),
            description=_("Remove vibrato in edited part, keep default vibrato in other parts"),
        ),
    ] = "hybrid"


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
