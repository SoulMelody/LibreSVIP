from pydantic import BaseModel, Field

from libresvip.model.option_mixins import (
    EnableInstrumentalTrackImportationMixin,
    EnablePitchImportationMixin,
    ExtractEmbededAudioMixin,
    StaticTempoMixin,
)
from libresvip.utils.translation import gettext_lazy as _

from .enums import PocketSingerLyricsLanguage


class InputOptions(
    EnableInstrumentalTrackImportationMixin,
    EnablePitchImportationMixin,
    ExtractEmbededAudioMixin,
    BaseModel,
):
    pass


class OutputOptions(StaticTempoMixin, BaseModel):
    lyric_language: PocketSingerLyricsLanguage = Field(
        default=PocketSingerLyricsLanguage.CHINESE,
        title=_("Lyrics language"),
    )
    title: str = Field(
        default="New Project",
        title=_("Title of the project"),
    )
