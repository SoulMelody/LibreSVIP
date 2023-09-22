from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field


class OffsetPolicyOption(Enum):
    TIMELINE: Annotated[
        str,
        Field(
            title="Act on timeline",
            description='Shift the time axis for each line of lyrics, and keep the "offset" value in the metadata at 0.',
        ),
    ] = "timeline"
    META: Annotated[
        str,
        Field(
            title="Act on metadata",
            description='Write the offset to the metadata "offset" without handling the lyrics time axis. Note that some players may not support the "offset" tag in the metadata, and choosing this option may cause the lyrics to display incorrectly.',
        ),
    ] = "meta"


class SplitOption(Enum):
    BOTH: Annotated[
        str,
        Field(
            title="Both note gap and punctuation",
            description="When the interval between two adjacent notes is greater than or equal to thirty-second note or a punctuation mark is encountered, start a new line.",
        ),
    ] = "both"
    GAP: Annotated[
        str,
        Field(
            title="Note gap only",
            description="When the interval between two adjacent notes is greater than or equal to thirty-second note, start a new line.",
        ),
    ] = "gap"
    SYMBOL: Annotated[
        str,
        Field(
            title="Punctuation only",
            description="When a punctuation mark is encountered, start a new line.",
        ),
    ] = "symbol"


class OutputOptions(BaseModel):
    artist: str = Field("", title="Singer name")
    title: str = Field("", title="Song title")
    album: str = Field("", title="Album name")
    by: str = Field("", title="Lyric editor")
    offset: int = Field(
        0,
        title="Offset",
        description="In milliseconds, positive means ahead, negative means opposite.",
    )
    offset_policy: OffsetPolicyOption = Field(
        title="Offset policy", default=OffsetPolicyOption.TIMELINE
    )
    split_by: SplitOption = Field(title="New line by", default=SplitOption.BOTH)
    timeline: bool = Field(
        title="Write timeline",
        description="If you need lyrics without timeline, turn off this option.",
        default=True,
    )
    encoding: str = Field(title="Lyric Text encoding", default="utf-8")
