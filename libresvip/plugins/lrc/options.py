from enum import Enum
from typing import Annotated

from pydantic import BaseSettings, Field


class OffsetPolicyOption(Enum):
    TIMELINE: Annotated[
        str,
        Field(title="作用于时间轴", description="对每一行歌词的时间轴作偏移，元数据的“offset”保持为0。")
    ] = 'timeline'
    META: Annotated[
        str,
        Field(title="作用于元数据", description="写入偏移量到元数据的“offset”，不处理歌词的时间轴。注意：由于部分播放器不支持元数据里的“offset”标签，选择此选项可能会导致歌词显示时间不准确。")
    ] = 'meta'


class SplitOption(Enum):
    BOTH: Annotated[
        str,
        Field(title='音符间隙和标点符号', description="两个相邻的音符间距大于等于32分音符或遇到标点符号时另起新行。")
    ] = 'both'
    GAP: Annotated[
        str,
        Field(title='仅音符间隙', description="两个相邻的音符间距大于等于32分音符时另起新行。")
    ] = 'gap'
    SYMBOL: Annotated[
        str,
        Field(title='仅标点符号', description="遇到标点符号时另起新行。")
    ] = 'symbol'


class OutputOptions(BaseSettings):
    artist: str = Field('', title="歌手名")
    title: str = Field('', title="歌曲名")
    album: str = Field('', title="专辑名")
    by: str = Field('', title="歌词作者")
    offset: int = Field(0, title="偏移量", description="单位为毫秒，正值表示整体提前，负值相反。")
    offset_policy: OffsetPolicyOption = Field(title="偏移处理方式", default=OffsetPolicyOption.TIMELINE)
    split_by: SplitOption = Field(title="歌词换行方式", default=SplitOption.BOTH)
    timeline: bool = Field(title="写入时间轴", description="如果需要无时间轴的歌词，关闭此选项即可。", default=True)
    encoding: str = Field(title="歌词文本编码", default="utf-8")
