from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field, create_model

from libresvip.utils.translation import gettext_lazy as _


class ProjectZoomOptions(Enum):
    _value_: Annotated[
        str,
        create_model(
            "ProjectZoomOptions",
            __module__="libresvip.middlewares.project_zoom.options",
            NONE=(str, Field(title=_("None"))),
            DOUBLE=(str, Field(title="2")),
            HALF=(str, Field(title=_("1/2"))),
            FIVE_THIRDS=(str, Field(title=_("5/3"))),
            THREE_HALVES=(str, Field(title=_("3/2"))),
            SIX_FIFTHS=(str, Field(title=_("6/5"))),
            FOUR_FIFTHS=(str, Field(title=_("4/5"))),
            THREE_FIFTHS=(str, Field(title=_("3/5"))),
            THREE_QUARTER=(str, Field(title=_("3/4"))),
        ),
    ]
    NONE = "1/1"
    DOUBLE = "2/1"
    HALF = "1/2"
    FIVE_THIRDS = "5/3"
    THREE_HALVES = "3/2"
    SIX_FIFTHS = "6/5"
    FOUR_FIFTHS = "4/5"
    THREE_FIFTHS = "3/5"
    THREE_QUARTER = "3/4"


class ProcessOptions(BaseModel):
    factor: ProjectZoomOptions = Field(
        default=ProjectZoomOptions.NONE,
        title=_("Zoom factor"),
        description=_(
            "Change Bpm and notes in parallel so that the actual singing speed is kept. For example, with factor 2, 60 bpm becomes 120 bpm and all notes become twice the length"
        ),
    )
