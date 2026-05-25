from pydantic import BaseModel, Field

from libresvip.model.option_mixins import (
    EnableInstrumentalTrackImportationMixin,
    EnablePitchImportationMixin,
    ExtractEmbededAudioMixin,
)
from libresvip.utils.translation import gettext_lazy as _


class InputOptions(
    EnableInstrumentalTrackImportationMixin,
    EnablePitchImportationMixin,
    ExtractEmbededAudioMixin,
    BaseModel,
):
    pass


class OutputOptions(BaseModel):
    default_singer_name: str = Field(
        "Default",
        title=_("Default Singer Name"),
        description=_("Default singer name for tracks without a singer"),
    )
