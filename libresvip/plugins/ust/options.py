from pydantic import Field

from libresvip.model.base import BaseModel
from libresvip.model.option_mixins import EnablePitchImportationMixin, SelectSingleTrackMixin


class InputOptions(EnablePitchImportationMixin, BaseModel):
    encoding: str = Field(
        default="SHIFT_JIS",
        title="Text encoding",
    )


class OutputOptions(SelectSingleTrackMixin, BaseModel):
    version: float = Field(
        default=1.2,
        title="Version",
        description="UST file version",
    )
    encoding: str = Field(
        default="SHIFT_JIS",
        title="Text encoding",
    )
