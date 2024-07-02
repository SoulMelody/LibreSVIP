from pydantic import BaseModel, Field

from libresvip.utils.translation import gettext_lazy as _


class ProcessOptions(BaseModel):
    key: int = Field(
        default=0,
        title=_("Key transition of pitch"),
        description=_("Pitch shift in semitones."),
    )
