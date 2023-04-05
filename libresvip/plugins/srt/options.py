from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field


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


class OutputOptions(BaseModel):
    offset: int = Field(0, title="偏移量", description="单位为毫秒，正值表示整体提前，负值相反。")
    split_by: SplitOption = Field(title="歌词换行方式", default=SplitOption.BOTH)
    encoding: str = Field(title="文本编码", default="utf-8")
