from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field, create_model

from libresvip.core.constants import TICKS_IN_BEAT
from libresvip.model.option_mixins import EnablePitchImportationMixin
from libresvip.utils.text import supported_charset_names
from libresvip.utils.translation import gettext_lazy as _


class BreathOption(Enum):
    _value_: Annotated[
        str,
        create_model(
            "BreathOption",
            __module__="libresvip.plugins.vsq.options",
            IGNORE=(str, Field(title=_("Ignore all breath notes"))),
            KEEP=(str, Field(title=_("Keep as normal notes"))),
        ),
    ]
    IGNORE = "ignore"
    KEEP = "keep"


class InputOptions(EnablePitchImportationMixin, BaseModel):
    lyric_encoding: str = Field(
        default="SHIFT_JIS",
        title=_("Lyric text encoding"),
        description=_("Unless the lyrics are garbled, this option should not be changed."),
        json_schema_extra={"enum": supported_charset_names()},
    )
    breath: BreathOption = Field(
        default=BreathOption.IGNORE,
        title=_("The way to handle breath notes"),
    )


class OutputOptions(BaseModel):
    ticks_per_beat: int = Field(
        default=TICKS_IN_BEAT,
        title=_("Ticks per beat"),
        description=_(
            "Also known as parts per quarter, ticks per quarter note, the number of pulses per quarter note. This setting should not be changed unless you know what it is."
        ),
    )
    lyric_encoding: str = Field(
        default="SHIFT_JIS",
        title=_("Lyric text encoding"),
        description=_("Unless the lyrics are garbled, this option should not be changed."),
        json_schema_extra={"enum": supported_charset_names()},
    )
