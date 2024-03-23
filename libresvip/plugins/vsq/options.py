from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field

from libresvip.model.option_mixins import EnablePitchImportationMixin


class BreathOption(Enum):
    IGNORE: Annotated[str, Field(title="Ignore all breath notes")] = "ignore"
    KEEP: Annotated[str, Field(title="Keep as normal notes")] = "keep"


class InputOptions(EnablePitchImportationMixin, BaseModel):
    lyric_encoding: str = Field(
        default="shift-jis",
        title="Lyric text encoding",
        description="Unless the lyrics are garbled, this option should not be changed.",
    )
    breath: BreathOption = Field(
        default=BreathOption.IGNORE,
        title="The way to handle breath notes",
    )


class OutputOptions(BaseModel):
    ticks_per_beat: int = Field(
        default=480,
        title="Ticks per beat",
        description="Also known as parts per quarter, ticks per quarter note, the number of pulses per quarter note. This setting should not be changed unless you know what it is.",
    )
    lyric_encoding: str = Field(
        default="shift-jis",
        title="Lyric text encoding",
        description="Unless the lyrics are garbled, this option should not be changed.",
    )
