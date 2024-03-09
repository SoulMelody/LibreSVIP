from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field


class NoteLengthOption(Enum):
    ZERO: Annotated[str, Field(title="Zero length note")] = "0/1"
    EIGHTH: Annotated[str, Field(title="1/8 note")] = "1/8"
    SIXTEENTH: Annotated[str, Field(title="1/16 note")] = "1/16"
    THIRTY_SECOND: Annotated[str, Field(title="1/32 note")] = "1/32"
    SIXTY_FOURTH: Annotated[str, Field(title="1/64 note")] = "1/64"
    ONE_HUNDRED_AND_TWENTY_EIGHTH: Annotated[
        str,
        Field(
            title="1/128 note",
        ),
    ] = "1/128"


class ProcessOptions(BaseModel):
    fill_threshold: NoteLengthOption = Field(
        default=NoteLengthOption.ZERO,
        title="Max length to be processed (exclusive)",
        description="Extend note to fill the short silences between it and its next note",
    )
