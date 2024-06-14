from gettext import gettext as _

from pydantic import BaseModel, Field

from libresvip.model.option_mixins import (
    EnablePitchImportationMixin,
    SelectSingleTrackMixin,
    StaticTempoMixin,
)


class InputOptions(EnablePitchImportationMixin, BaseModel):
    pass


class OutputOptions(SelectSingleTrackMixin, StaticTempoMixin, BaseModel):
    version: int = Field(
        default=19,
        title=_("Version"),
        description=_("Version of NIAONiao project file"),
    )
