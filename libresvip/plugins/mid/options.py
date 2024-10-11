from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field

from libresvip.core.constants import DEFAULT_BPM
from libresvip.model.option_mixins import (
    EnablePitchImportationMixin,
    EnableVolumeImportationMixin,
)
from libresvip.utils.translation import gettext_lazy as _


class MultiChannelOption(Enum):
    FIRST: Annotated[str, Field(title=_("Import first channel only"))] = "first"
    SPLIT: Annotated[str, Field(title=_("Split into tracks"))] = "split"
    CUSTOM: Annotated[str, Field(title=_("Custom import range"))] = "custom"


class InputOptions(EnablePitchImportationMixin, EnableVolumeImportationMixin, BaseModel):
    import_lyrics: bool = Field(default=True, title=_("Import lyrics"))
    lyric_encoding: str = Field(
        default="utf-8",
        title=_("Lyric text encoding"),
        description=_("Unless the lyrics are garbled, this option should not be changed."),
    )
    import_time_signatures: bool = Field(
        default=True,
        title=_("Import time signatures"),
        description=_("If this option is unset, the time signature is set to 4/4."),
    )
    multi_channel: MultiChannelOption = Field(
        default=MultiChannelOption.FIRST,
        title=_("Multi-channel processing method"),
    )
    channels: str = Field(
        default="1",
        title=_("Channels to import"),
        description=_(
            'Specify which channels to import notes from. Enter channel numbers and/or channel ranges (separated by commas), e.g. 1,3,5-12. Range: 1-16. Only valid when the option "Custom import range" is selected in "Multi-channel processing method".'
        ),
    )
    default_bpm: float = Field(
        default=DEFAULT_BPM,
        title=_("Default BPM"),
        description=_("Used when no BPM information is found in the MIDI file."),
    )


class OutputOptions(BaseModel):
    export_lyrics: bool = Field(default=True, title=_("Export lyrics"))
    remove_symbols: bool = Field(
        default=True,
        title=_("Remove symbols from lyrics"),
        description=_(
            "Remove commas, periods, question marks and exclamation marks in Chinese and English to prevent lyric import failure in some vocal synthesizers."
        ),
    )
    compatible_lyric: bool = Field(
        default=False,
        title=_("Lyric compatibility mode"),
        description=_(
            "Convert all Chinese lyrics to pinyin to prevent garbled characters in MIDI files with Chinese lyrics from being imported by vocal synthesizers that do not support Chinese lyrics."
        ),
    )
    lyric_encoding: str = Field(
        default="utf-8",
        title=_("Lyric text encoding"),
        description=_("Unless the lyrics are garbled, this option should not be changed."),
    )
    transpose: int = Field(
        default=0,
        title=_("Transpose"),
    )
    ticks_per_beat: int = Field(
        default=480,
        title=_("Ticks per beat"),
        description=_(
            "Also known as parts per quarter, ticks per quarter note, the number of pulses per quarter note. This setting should not be changed unless you know what it is."
        ),
    )
