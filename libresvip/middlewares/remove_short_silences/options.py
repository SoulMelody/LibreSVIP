from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field, create_model

from libresvip.utils.translation import gettext_lazy as _


class NoteLengthOption(Enum):
    _value_: Annotated[
        str,
        create_model(
            "NoteLengthOption",
            __module__="libresvip.middlewares.remove_short_silences.options",
            ZERO=(str, Field(title=_("Zero length note"))),
            EIGHTH=(str, Field(title=_("1/8 note"))),
            SIXTEENTH=(str, Field(title=_("1/16 note"))),
            THIRTY_SECOND=(str, Field(title=_("1/32 note"))),
            SIXTY_FOURTH=(str, Field(title=_("1/64 note"))),
            ONE_HUNDRED_AND_TWENTY_EIGHTH=(str, Field(title=_("1/128 note"))),
        ),
    ]
    ZERO = "0/1"
    EIGHTH = "1/8"
    SIXTEENTH = "1/16"
    THIRTY_SECOND = "1/32"
    SIXTY_FOURTH = "1/64"
    ONE_HUNDRED_AND_TWENTY_EIGHTH = "1/128"


class ProcessOptions(BaseModel):
    fill_threshold: NoteLengthOption = Field(
        default=NoteLengthOption.ZERO,
        title=_("Max length to be processed (exclusive)"),
        description=_("Extend note to fill the short silences between it and its next note"),
    )
