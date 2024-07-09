from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field

from libresvip.utils.translation import gettext_lazy as _


class ProjectZoomOptions(Enum):
    NONE: Annotated[str, Field(title=_("None"))] = "1/1"
    DOUBLE: Annotated[str, Field(title="2")] = "2/1"
    HALF: Annotated[str, Field(title=_("1/2"))] = "1/2"
    FIVE_THIRDS: Annotated[str, Field(title=_("5/3"))] = "5/3"
    THREE_HALVES: Annotated[str, Field(title=_("3/2"))] = "3/2"
    SIX_FIFTHS: Annotated[str, Field(title=_("6/5"))] = "6/5"
    FOUR_FIFTHS: Annotated[str, Field(title=_("4/5"))] = "4/5"
    THREE_FIFTHS: Annotated[str, Field(title=_("3/5"))] = "3/5"
    THREE_QUARTER: Annotated[str, Field(title=_("3/4"))] = "3/4"


class ProcessOptions(BaseModel):
    factor: ProjectZoomOptions = Field(
        default=ProjectZoomOptions.NONE,
        title=_("Zoom factor"),
        description=_(
            "Change Bpm and notes in parallel so that the actual singing speed is kept. For example, with factor 2, 60 bpm becomes 120 bpm and all notes become twice the length"
        ),
    )
