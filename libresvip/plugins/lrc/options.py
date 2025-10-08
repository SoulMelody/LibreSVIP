from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field, create_model

from libresvip.utils.text import supported_charset_names
from libresvip.utils.translation import gettext_lazy as _


class OffsetPolicyOption(Enum):
    _value_: Annotated[
        str,
        create_model(
            "OffsetPolicyOption",
            __module__="libresvip.plugins.lrc.options",
            TIMELINE=(
                str,
                Field(
                    title=_("Act on timeline"),
                    description=_(
                        'Shift the time axis for each line of lyrics, and keep the "offset" value in the metadata at 0.'
                    ),
                ),
            ),
            META=(
                str,
                Field(
                    title=_("Act on metadata"),
                    description=_(
                        'Write the offset to the metadata "offset" without handling the lyrics time axis. Note that some players may not support the "offset" tag in the metadata, and choosing this option may cause the lyrics to display incorrectly.'
                    ),
                ),
            ),
        ),
    ]
    TIMELINE = "timeline"
    META = "meta"


class SplitOption(Enum):
    _value_: Annotated[
        str,
        create_model(
            "SplitOption",
            __module__="libresvip.plugins.lrc.options",
            BOTH=(
                str,
                Field(
                    title=_("Both note gap and punctuation"),
                    description=_(
                        "When the interval between two adjacent notes is greater than or equal to thirty-second note or a punctuation mark is encountered, start a new line."
                    ),
                ),
            ),
            GAP=(
                str,
                Field(
                    title=_("Note gap only"),
                    description=_(
                        "When the interval between two adjacent notes is greater than or equal to thirty-second note, start a new line."
                    ),
                ),
            ),
            SYMBOL=(
                str,
                Field(
                    title=_("Punctuation only"),
                    description=_("When a punctuation mark is encountered, start a new line."),
                ),
            ),
        ),
    ]
    BOTH = "both"
    GAP = "gap"
    SYMBOL = "symbol"


class OutputOptions(BaseModel):
    artist: str = Field("", title=_("Singer name"))
    title: str = Field("", title=_("Song title"))
    album: str = Field("", title=_("Album name"))
    by: str = Field("", title=_("Lyric editor"))
    offset: int = Field(
        0,
        title=_("Offset"),
        description=_("In milliseconds, positive means ahead, negative means opposite."),
    )
    offset_policy: OffsetPolicyOption = Field(
        title=_("Offset policy"), default=OffsetPolicyOption.TIMELINE
    )
    split_by: SplitOption = Field(title=_("New line by"), default=SplitOption.BOTH)
    ignore_slur_notes: bool = Field(
        title=_("Ignore slur notes"),
        description=_(
            "Ignore '-' lyrics that are used to indicate slur notes in singing synthesizers."
        ),
        default=True,
    )
    timeline: bool = Field(
        title=_("Write timeline"),
        description=_("If you need lyrics without timeline, turn off this option."),
        default=True,
    )
    encoding: str = Field(
        title=_("Lyric Text encoding"),
        default="utf-8",
        json_schema_extra={"enum": supported_charset_names()},
    )
