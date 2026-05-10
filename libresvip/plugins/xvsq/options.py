from pydantic import BaseModel, Field

from libresvip.model.option_mixins import (
    EnableBreathImportationMixin,
    EnableGenderImportationMixin,
    EnableInstrumentalTrackImportationMixin,
    EnablePitchImportationMixin,
    EnableStrengthImportationMixin,
    EnableVolumeImportationMixin,
)
from libresvip.utils.translation import gettext_lazy as _


class InputOptions(
    EnableInstrumentalTrackImportationMixin,
    EnablePitchImportationMixin,
    EnableVolumeImportationMixin,
    EnableBreathImportationMixin,
    EnableGenderImportationMixin,
    EnableStrengthImportationMixin,
    BaseModel,
):
    pass


class OutputOptions(BaseModel):
    pretty_xml: bool = Field(
        True,
        title=_("Pretty XML"),
        description=_("Whether to output pretty XML"),
    )
