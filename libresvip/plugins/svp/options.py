from enum import Enum
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


class LanguageOption(Enum):
    MANDARIN: Annotated[str, Field(title="Mandarin")] = "mandarin"
    CANTONESE: Annotated[str, Field(title="Cantonese")] = "cantonese"
    JAPANESE: Annotated[str, Field(title="Japanese")] = "japanese"
    ENGLISH: Annotated[str, Field(title="English")] = "english"
    SPANISH: Annotated[str, Field(title="Spanish")] = "spanish"


class BreathOption(Enum):
    IGNORE: Annotated[str, Field(title="Ignore all breath notes")] = "ignore"
    KEEP: Annotated[str, Field(title="Keep as normal notes")] = "keep"
    CONVERT: Annotated[str, Field(title="Convert to breath mark")] = "convert"


class GroupOption(Enum):
    SPLIT: Annotated[
        str,
        Field(
            title="Split all to tracks",
            description="Generate a track for each note group reference",
        ),
    ] = "split"
    MERGE: Annotated[
        str,
        Field(
            title="Keep original position",
            description="Split note groups to separate tracks only when notes overlap",
        ),
    ] = "merge"


class PitchOption(Enum):
    FULL: Annotated[
        str,
        Field(
            title="Full pitch curve",
            description="Input the full pitch curve regardless of editing",
        ),
    ] = "full"
    VIBRATO: Annotated[
        str,
        Field(
            title="Edited part only (vibrato mode)",
            description="Input the edited part of pitch curve; default vibrato will be imported if not edited",
        ),
    ] = "vibrato"
    PLAIN: Annotated[
        str,
        Field(
            title="Edited part only (plain mode)",
            description="Input the edited part of pitch curve; default vibrato will be ignored",
        ),
    ] = "plain"


class VibratoOption(Enum):
    NONE: Annotated[
        str,
        Field(
            title="All removed",
            description="All notes will be set to 0 vibrato depth to ensure the output pitch curve is the same as input",
        ),
    ] = "none"
    ALWAYS: Annotated[
        str,
        Field(
            title="All kept",
            description="Keep all notes' default vibrato, but may cause inconsistent pitch curves",
        ),
    ] = "always"
    HYBRID: Annotated[
        str,
        Field(
            title="Hybrid mode",
            description="Remove vibrato in edited part, keep default vibrato in other parts",
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
        title="Always follow instant pitch mode",
        description="When this option is turned off, the default pitch curve will always be imported regardless of the project setting. If you have tuned the pitch curve based on instant pitch mode, it is recommended to turn on this option.",
    )
    pitch: PitchOption = Field(
        default=PitchOption.PLAIN,
        title="Pitch input mode",
        description='This option controls the range of pitch curve to be imported and the judgment condition. The definition of "edited part" is: the pitch deviation in the parameter panel, the pitch transition in the vibrato envelope and the pitch transition in the note properties have been edited.',
    )
    breath: BreathOption = Field(
        default=BreathOption.CONVERT,
        title="The way to handle breath notes",
    )
    group: GroupOption = Field(
        default=GroupOption.SPLIT,
        title="The way to handle note groups",
        description='Notice: If there are too many note groups, please choose "Keep original position" to avoid excessive track count. But if there are notes that are adjacent (but not overlapped) between note groups or between note groups and main group, it is recommended to choose "Split to tracks" to ensure the paragraph division is not broken.',
    )


class OutputOptions(BaseModel):
    vibrato: VibratoOption = Field(
        default=VibratoOption.NONE, title="The way to handle vibrato notes"
    )
    down_sample: int = Field(
        default=40,
        title="Set the average sampling interval of parameter points to improve performance (0 means no limit)",
        description="Reduce the sampling interval to improve the accuracy of parameter curves, but may cause rendering lag (e.g. Synthesizer V Studio Pro + AI voicebank). Please set this value according to your hardware configuration and actual experience.",
    )
    language_override: LanguageOption = Field(
        default=LanguageOption.MANDARIN,
        title="Override default language for the voicebank",
    )
