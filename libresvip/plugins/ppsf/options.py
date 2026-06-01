from pydantic import BaseModel, Field

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


class OutputOptions(BaseModel):
    use_legacy_format: bool = Field(
        False,
        title=_("Export as legacy format"),
        description=_(
            "Export in the legacy binary PPSF format instead of the newer ZIP-based JSON format"
        ),
    )
