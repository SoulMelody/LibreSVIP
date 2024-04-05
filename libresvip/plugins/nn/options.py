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
        title="Version",
        description="Version of NIAONiao project file",
    )
