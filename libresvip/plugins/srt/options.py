from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field


class SplitOption(Enum):
    BOTH: Annotated[
        str,
        Field(
            title="Both note gap and punctuation",
            description="两个相邻的音符间距大于等于32分音符或遇到标点符号时另起新行。",
        ),
    ] = "both"
    GAP: Annotated[
        str, Field(title="Note gap only", description="两个相邻的音符间距大于等于32分音符时另起新行。")
    ] = "gap"
    SYMBOL: Annotated[
        str, Field(title="Punctuation only", description="遇到标点符号时另起新行。")
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
