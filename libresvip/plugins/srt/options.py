from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field

from libresvip.model.option_mixins import SelectSingleTrackMixin
from libresvip.utils.translation import gettext_lazy as _


class SplitOption(Enum):
    BOTH: Annotated[
        str,
        Field(
            title=_("Both note gap and punctuation"),
            description=_(
                "When the interval between two adjacent notes is greater than or equal to thirty-second note or a punctuation mark is encountered, start a new line."
            ),
        ),
    ] = "both"
    GAP: Annotated[
        str,
        Field(
            title=_("Note gap only"),
            description=_(
                "When the interval between two adjacent notes is greater than or equal to thirty-second note, start a new line."
            ),
        ),
    ] = "gap"
    SYMBOL: Annotated[
        str,
        Field(
            title=_("Punctuation only"),
            description=_("When a punctuation mark is encountered, start a new line."),
        ),
    ] = "symbol"


class OutputOptions(SelectSingleTrackMixin, BaseModel):
    offset: int = Field(
        0,
        title=_("Offset"),
        description=_("In milliseconds, positive means ahead, negative means opposite."),
    )
    split_by: SplitOption = Field(title=_("New line by"), default=SplitOption.BOTH)
    encoding: str = Field(title=_("Text encoding"), default="utf-8")
