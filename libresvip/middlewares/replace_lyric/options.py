from pydantic import BaseModel, Field

from libresvip.utils.translation import gettext_lazy as _


class ProcessOptions(BaseModel):
    lyric_replacement_preset_name: str = Field(
        default="default",
        title=_("Name of lyric replacement preset"),
    )
