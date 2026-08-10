from enum import Enum

from pydantic import BaseModel, Field

from libresvip.model.option_mixins import (
    EnableInstrumentalTrackImportationMixin,
    EnablePitchImportationMixin,
)
from libresvip.utils.translation import gettext_lazy as _


class BpmSource(str, Enum):
    AUTOMATIC = "automatic"
    SONG_INFO = "song_info"
    BGM_INFO = "bgm_info"


class InputOptions(
    EnableInstrumentalTrackImportationMixin,
    EnablePitchImportationMixin,
    BaseModel,
):
    bpm_source: BpmSource = Field(
        default=BpmSource.AUTOMATIC,
        title=_("BPM source"),
        description=_(
            "Use the accompaniment BPM when it is present, or fall back to the song BPM."
        ),
    )


class OutputOptions(BaseModel):
    author: str = Field(default="", title=_("Author"))
    export_pitch: bool = Field(default=True, title=_("Export pitch curve"))
    indented: bool = Field(default=True, title=_("Indent JSON"))
    key: str = Field(default="C", title=_("Musical key"))
    role_id: int = Field(default=0, title=_("Default mobile singer ID"))
    role_name: str = Field(default="", title=_("Default mobile singer name"))
    song_name: str = Field(default="New Project", title=_("Song name"))
