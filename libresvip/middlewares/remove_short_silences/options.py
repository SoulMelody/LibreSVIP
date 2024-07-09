from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field

from libresvip.utils.translation import gettext_lazy as _


class NoteLengthOption(Enum):
    ZERO: Annotated[str, Field(title=_("Zero length note"))] = "0/1"
    EIGHTH: Annotated[str, Field(title=_("1/8 note"))] = "1/8"
    SIXTEENTH: Annotated[str, Field(title=_("1/16 note"))] = "1/16"
    THIRTY_SECOND: Annotated[str, Field(title=_("1/32 note"))] = "1/32"
    SIXTY_FOURTH: Annotated[str, Field(title=_("1/64 note"))] = "1/64"
    ONE_HUNDRED_AND_TWENTY_EIGHTH: Annotated[
        str,
        Field(
            title=_("1/128 note"),
        ),
    ] = "1/128"


class ProcessOptions(BaseModel):
    fill_threshold: NoteLengthOption = Field(
        default=NoteLengthOption.ZERO,
        title=_("Max length to be processed (exclusive)"),
        description=_("Extend note to fill the short silences between it and its next note"),
    )
