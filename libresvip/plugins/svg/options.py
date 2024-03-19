from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field
from pydantic_extra_types.color import Color


class TextAlignOption(Enum):
    START: Annotated[str, Field(title="Align to left")] = "start"
    MIDDLE: Annotated[str, Field(title="Align to middle")] = "middle"
    END: Annotated[str, Field(title="Align to right")] = "end"


class TextPositionOption(Enum):
    UPPER: Annotated[str, Field(title="Above the note")] = "upper"
    INNER: Annotated[str, Field(title="Inside the note")] = "inner"
    LOWER: Annotated[str, Field(title="Below the note")] = "lower"
    NONE: Annotated[str, Field(title="Don't show")] = "none"


class OutputOptions(BaseModel):
    pixel_per_beat: int = Field(48, title="Pixels per beat", description="Unit: pixel.")
    note_height: int = Field(24, title="Note height", description="Unit: pixel.")
    note_round: int = Field(4, title="Note radius", description="Unit: pixel.")
    note_fill_color: Color = Field(
        "#CCFFCC",
        title="Note fill color",
        description="CSS color value, e.g. #FF0000, #66CCFF, rgba(255,0,0,0.5), etc.",
    )
    note_stroke_color: Color = Field(
        "#006600",
        title="Note stroke color",
        description="CSS color value, e.g. #FF0000, #66CCFF, rgba(255,0,0,0.5), etc.",
    )
    note_stroke_width: int = Field(1, title="Note stroke width", description="Unit: pixel.")
    pitch_stroke_color: Color = Field(
        "#99aa99",
        title="Pitch stroke color",
        description="CSS color value, e.g. #FF0000, #66CCFF, rgba(255,0,0,0.5), etc.",
    )
    pitch_stroke_width: int = Field(2, title="Pitch stroke width", description="Unit: pixel.")
    lyric_position: TextPositionOption = Field(
        TextPositionOption.LOWER,
        title="Lyric position",
    )
    pronounciation_position: TextPositionOption = Field(
        TextPositionOption.INNER,
        title="Pronounciation position",
    )
    text_align: TextAlignOption = Field(
        TextAlignOption.START,
        title="Text align",
    )
    inner_text_color: Color = Field(
        "#000000",
        title="Inner text color",
        description="CSS color value, e.g. #FF0000, #66CCFF, rgba(255,0,0,0.5), etc.",
    )
    side_text_color: Color = Field(
        "#000000",
        title="The color of the text on the top and bottom of the note",
        description="CSS color value, e.g. #FF0000, #66CCFF, rgba(255,0,0,0.5), etc.",
    )
    track_index: int = Field(
        default=-1,
        title="Track index",
        description="Start from 0, -1 means auto select",
    )
    show_grid: bool = Field(default=False, title="Show grid lines")
    grid_color: Color = Field(
        "#CCCCCC",
        title="Grid line color",
        description="CSS color value, e.g. #FF0000, #66CCFF, rgba(255,0,0,0.5), etc.",
    )
    grid_stroke_width: int = Field(1, title="Grid line width", description="Unit: pixel.")
