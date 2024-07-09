from pydantic import BaseModel, Field

from libresvip.model.option_mixins import (
    EnablePitchImportationMixin,
    SelectSingleTrackMixin,
    StaticTempoMixin,
)
from libresvip.utils.translation import gettext_lazy as _


class InputOptions(EnablePitchImportationMixin, BaseModel):
    pass


class OutputOptions(SelectSingleTrackMixin, StaticTempoMixin, BaseModel):
    version: int = Field(
        default=19,
        title=_("Version"),
        description=_("Version of NIAONiao project file"),
    )
