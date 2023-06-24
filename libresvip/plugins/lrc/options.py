from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field


class OffsetPolicyOption(Enum):
    TIMELINE: Annotated[
        str,
        Field(title="Act on timeline", description="对每一行歌词的时间轴作偏移，元数据的“offset”保持为0。"),
    ] = "timeline"
    META: Annotated[
        str,
        Field(
            title="Act on metadata",
            description="写入偏移量到元数据的“offset”，不处理歌词的时间轴。注意：由于部分播放器不支持元数据里的“offset”标签，选择此选项可能会导致歌词显示时间不准确。",
        ),
    ] = "meta"


class SplitOption(Enum):
    BOTH: Annotated[
        str,
        Field(
            title="Both notes gap and punctuation",
            description="两个相邻的音符间距大于等于32分音符或遇到标点符号时另起新行。",
        ),
    ] = "both"
    GAP: Annotated[
        str, Field(title="Notes gap only", description="两个相邻的音符间距大于等于32分音符时另起新行。")
    ] = "gap"
    SYMBOL: Annotated[
        str, Field(title="Punctuation only", description="遇到标点符号时另起新行。")
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
