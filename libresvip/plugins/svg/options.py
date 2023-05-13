from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field
from pydantic.color import Color


class TextAlignOption(Enum):
    START: Annotated[str, Field(title="左对齐")] = "start"
    MIDDLE: Annotated[str, Field(title="居中对齐")] = "middle"
    END: Annotated[str, Field(title="右对齐")] = "end"


class TextPositionOption(Enum):
    UPPER: Annotated[str, Field(title="音符上方")] = "upper"
    INNER: Annotated[str, Field(title="音符内部")] = "inner"
    LOWER: Annotated[str, Field(title="音符下方")] = "lower"
    NONE: Annotated[str, Field(title="不显示")] = "none"


class OutputOptions(BaseModel):
    pixel_per_beat: int = Field(48, title="每拍长度", description="单位：像素。")
    note_height: int = Field(24, title="音符高度", description="单位：像素。")
    note_round: int = Field(4, title="音符圆角", description="单位：像素。")
    note_fill_color: Color = Field(
        "#CCFFCC",
        title="音符填充颜色",
        description="CSS 颜色值，例如：#FF0000，#66CCFF，rgba(255,0,0,0.5) 等。",
    )
    note_stroke_color: Color = Field(
        "#006600",
        title="音符描边颜色",
        description="CSS 颜色值，例如：#FF0000，#66CCFF，rgba(255,0,0,0.5) 等。",
    )
    note_stroke_width: int = Field(1, title="音符描边宽度", description="单位：像素。")
    pitch_stroke_color: Color = Field(
        "#99aa99",
        title="音高曲线描边颜色",
        description="CSS 颜色值，例如：#FF0000，#66CCFF，rgba(255,0,0,0.5) 等。",
    )
    pitch_stroke_width: int = Field(2, title="音高曲线描边宽度", description="单位：像素。")
    lyric_position: TextPositionOption = Field(
        TextPositionOption.LOWER,
        title="歌词显示于",
    )
    pronounciation_position: TextPositionOption = Field(
        TextPositionOption.INNER,
        title="发音显示于",
    )
    text_align: TextAlignOption = Field(
        TextAlignOption.START,
        title="文字对齐",
    )
    inner_text_color: Color = Field(
        "#000000",
        title="音符内部文本颜色",
        description="CSS 颜色值，例如：#FF0000，#66CCFF，rgba(255,0,0,0.5) 等。",
    )
    side_text_color: Color = Field(
        "#000000",
        title="音符上下方文本颜色",
        description="CSS 颜色值，例如：#FF0000，#66CCFF，rgba(255,0,0,0.5) 等。",
    )
    track_index: int = Field(default=-1, title="演唱轨序号", description="从0开始，-1表示自动选择")
    show_grid: bool = Field(default=False, title="显示网格线")
    grid_color: Color = Field(
        "#CCCCCC",
        title="网格线颜色",
        description="CSS 颜色值，例如：#FF0000，#66CCFF，rgba(255,0,0,0.5) 等。",
    )
    grid_stroke_width: int = Field(1, title="网格线宽度", description="单位：像素。")
