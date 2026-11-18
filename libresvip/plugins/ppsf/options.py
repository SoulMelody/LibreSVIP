from enum import IntEnum
from typing import Annotated

from pydantic import BaseModel, Field, create_model

from libresvip.model.option_mixins import (
    EnableInstrumentalTrackImportationMixin,
    EnablePitchImportationMixin,
)
from libresvip.utils.translation import gettext_lazy as _


class InputOptions(
    EnableInstrumentalTrackImportationMixin,
    EnablePitchImportationMixin,
    BaseModel,
):
    pass


class PpsfProjectVersionCompatibility(IntEnum):
    _value_: Annotated[
        int,
        create_model(
            "PpsfProjectVersionCompatibility",
            __module__="libresvip.plugins.ppsf.options",
            LEGACY_PPSF=(
                int,
                Field(title=_("Legacy binary format")),
            ),
            BELOW_1_3_0=(
                int,
                Field(title=_("Compatible with Piapro Studio NT2 1.2.2.2 and below")),
            ),
            ABOVE_1_3_0=(
                int,
                Field(title=_("Compatible with Piapro Studio NT2 1.3.0 and up")),
            ),
        ),
    ]
    LEGACY_PPSF = 100
    BELOW_1_3_0 = 1222
    ABOVE_1_3_0 = 1300


class OutputOptions(BaseModel):
    version_compatibility: PpsfProjectVersionCompatibility = Field(
        PpsfProjectVersionCompatibility.BELOW_1_3_0,
        title=_("Project file version"),
        description=_(
            "Pick the Piapro Studio version you will open the project with. The project layout "
            "below 1.3.0 is also readable by 1.3.0 and keeps the pitch closer to the imported "
            "curve; the 1.3.0 layout stores the pitch as per-note f0 points and lets the engine "
            "smooth it more. The legacy binary format targets very old versions."
        ),
    )
