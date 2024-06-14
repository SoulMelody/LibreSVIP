from gettext import gettext as _

from pydantic import BaseModel, Field


class ProcessOptions(BaseModel):
    lyric_replacement_preset_name: str = Field(
        default="default",
        title=_("Name of lyric replacement preset"),
    )
