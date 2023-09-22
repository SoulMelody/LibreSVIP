from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field


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
    offset: int = Field(
        0,
        title="Offset",
        description="In milliseconds, positive means ahead, negative means opposite.",
    )
    split_by: SplitOption = Field(title="New line by", default=SplitOption.BOTH)
    encoding: str = Field(title="Text encoding", default="utf-8")
    track_index: int = Field(
        default=-1,
        title="Track index",
        description="Start from 0, -1 means automatic selection",
    )
