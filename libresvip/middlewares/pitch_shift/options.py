from gettext import gettext as _

from pydantic import BaseModel, Field


class ProcessOptions(BaseModel):
    key: int = Field(
        default=0,
        title=_("Key transition of pitch"),
        description=_("Pitch shift in semitones."),
    )
