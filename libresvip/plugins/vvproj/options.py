from pydantic import BaseModel, Field

from libresvip.core.constants import DEFAULT_BPM
from libresvip.model.option_mixins import (
    EnablePitchImportationMixin,
)
from libresvip.utils.translation import gettext_lazy as _


class InputOptions(EnablePitchImportationMixin, BaseModel):
    pass


class OutputOptions(BaseModel):
    tempo: int = Field(
        default=int(DEFAULT_BPM),
        title=_("Constant tempo"),
        description=_("Use this tempo to reset time axis of projects with dynamic tempos"),
    )
