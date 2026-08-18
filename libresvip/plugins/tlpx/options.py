from enum import IntEnum
from typing import Annotated

from pydantic import BaseModel, Field, create_model

from libresvip.model.option_mixins import (
    EnableInstrumentalTrackImportationMixin,
    EnablePitchImportationMixin,
)
from libresvip.utils.translation import gettext_lazy as _


class TuneLabVersionCompatibility(IntEnum):
    _value_: Annotated[
        int,
        create_model(
            "TuneLabVersionCompatibility",
            __module__="libresvip.plugins.tlpx.options",
            LEGACY=(
                int,
                Field(
                    title=_("TLPX v0 (legacy)"),
                    description=_("Use the legacy part format with a single duration."),
                ),
            ),
            CURRENT=(
                int,
                Field(
                    title=_("TLPX v1 (current)"),
                    description=_("Use the current part format with start/end offsets."),
                ),
            ),
        ),
    ]
    LEGACY = 0
    CURRENT = 1


class InputOptions(
    EnableInstrumentalTrackImportationMixin,
    EnablePitchImportationMixin,
    BaseModel,
):
    pass


class OutputOptions(BaseModel):
    version_compatibility: TuneLabVersionCompatibility = Field(
        default=TuneLabVersionCompatibility.CURRENT,
        title=_("TLPX version compatibility"),
        description=_("Choose the version written when exporting TLPX."),
    )
