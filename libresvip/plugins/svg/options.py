from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field
from pydantic_extra_types.color import Color

from libresvip.model.option_mixins import SelectSingleTrackMixin
from libresvip.utils.translation import gettext_lazy as _


class TextAlignOption(Enum):
    START: Annotated[str, Field(title=_("Align to left"))] = "start"
    MIDDLE: Annotated[str, Field(title=_("Align to middle"))] = "middle"
    END: Annotated[str, Field(title=_("Align to right"))] = "end"


class TextPositionOption(Enum):
    UPPER: Annotated[str, Field(title=_("Above the note"))] = "upper"
    INNER: Annotated[str, Field(title=_("Inside the note"))] = "inner"
    LOWER: Annotated[str, Field(title=_("Below the note"))] = "lower"
    NONE: Annotated[str, Field(title=_("Don't show"))] = "none"


class OutputOptions(SelectSingleTrackMixin, BaseModel):
    pixel_per_beat: int = Field(48, title=_("Pixels per beat"), description=_("Unit: pixel."))
    note_height: int = Field(24, title=_("Note height"), description=_("Unit: pixel."))
    note_round: int = Field(4, title=_("Note radius"), description="Unit: pixel.")
    note_fill_color: Color = Field(
        "#CCFFCC",
        title=_("Note fill color"),
        description=_("CSS color value, e.g. #FF0000, #66CCFF, rgba(255,0,0,0.5), etc."),
    )
    note_stroke_color: Color = Field(
        "#006600",
        title=_("Note stroke color"),
        description=_("CSS color value, e.g. #FF0000, #66CCFF, rgba(255,0,0,0.5), etc."),
    )
    note_stroke_width: int = Field(1, title="Note stroke width", description="Unit: pixel.")
    pitch_stroke_color: Color = Field(
        "#99aa99",
        title=_("Pitch stroke color"),
        description=_("CSS color value, e.g. #FF0000, #66CCFF, rgba(255,0,0,0.5), etc."),
    )
    pitch_stroke_width: int = Field(2, title=_("Pitch stroke width"), description=_("Unit: pixel."))
    lyric_position: TextPositionOption = Field(
        TextPositionOption.LOWER,
        title=_("Lyric position"),
    )
    pronounciation_position: TextPositionOption = Field(
        TextPositionOption.INNER,
        title=_("Pronounciation position"),
    )
    text_align: TextAlignOption = Field(
        TextAlignOption.START,
        title=_("Text align"),
    )
    inner_text_color: Color = Field(
        "#000000",
        title=_("Inner text color"),
        description=_("CSS color value, e.g. #FF0000, #66CCFF, rgba(255,0,0,0.5), etc."),
    )
    side_text_color: Color = Field(
        "#000000",
        title=_("The color of the text on the top and bottom of the note"),
        description=_("CSS color value, e.g. #FF0000, #66CCFF, rgba(255,0,0,0.5), etc."),
    )
    show_grid: bool = Field(default=False, title="Show grid lines")
    grid_color: Color = Field(
        "#CCCCCC",
        title=_("Grid line color"),
        description=_("CSS color value, e.g. #FF0000, #66CCFF, rgba(255,0,0,0.5), etc."),
    )
    grid_stroke_width: int = Field(1, title=_("Grid line width"), description=_("Unit: pixel."))
