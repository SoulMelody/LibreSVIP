from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field

from libresvip.core.constants import DEFAULT_BPM
from libresvip.model.option_mixins import EnablePitchImportationMixin, EnableVolumeImportationMixin


class MultiChannelOption(Enum):
    FIRST: Annotated[str, Field(title="Import first channel only")] = "first"
    SPLIT: Annotated[str, Field(title="Split into tracks")] = "split"
    CUSTOM: Annotated[str, Field(title="Custom import range")] = "custom"


class InputOptions(EnablePitchImportationMixin, EnableVolumeImportationMixin, BaseModel):
    import_lyrics: bool = Field(default=True, title="Import lyrics")
    lyric_encoding: str = Field(
        default="utf-8",
        title="Lyric text encoding",
        description="Unless the lyrics are garbled, this option should not be changed.",
    )
    import_time_signatures: bool = Field(
        default=True,
        title="Import time signatures",
        description="If this option is unset, the time signature is set to 4/4.",
    )
    multi_channel: MultiChannelOption = Field(
        default=MultiChannelOption.FIRST,
        title="Multi-channel processing method",
    )
    channels: str = Field(
        default="1",
        title="Channels to import",
        description='Specify which channels to import notes from. Enter channel numbers and/or channel ranges (separated by commas), e.g. 1,3,5-12. Range: 1-16. Only valid when the option "Custom import range" is selected in "Multi-channel processing method".',
    )
    default_bpm: float = Field(
        default=DEFAULT_BPM,
        title="Default BPM",
        description="Used when no BPM information is found in the MIDI file.",
    )


class OutputOptions(BaseModel):
    export_lyrics: bool = Field(default=True, title="Export lyrics")
    remove_symbols: bool = Field(
        default=True,
        title="Remove symbols from lyrics",
        description="Remove commas, periods, question marks and exclamation marks in Chinese and English to prevent lyric import failure in some vocal synthesizers.",
    )
    compatible_lyric: bool = Field(
        default=False,
        title="Lyric compatibility mode",
        description="Convert all Chinese lyrics to pinyin to prevent garbled characters in MIDI files with Chinese lyrics from being imported by vocal synthesizers that do not support Chinese lyrics.",
    )
    lyric_encoding: str = Field(
        default="utf-8",
        title="Lyric text encoding",
        description="Unless the lyrics are garbled, this option should not be changed.",
    )
    transpose: int = Field(
        default=0,
        title="Transpose",
    )
    ticks_per_beat: int = Field(
        default=480,
        title="Ticks per beat",
        description="Also known as parts per quarter, ticks per quarter note, the number of pulses per quarter note. This setting should not be changed unless you know what it is.",
    )
