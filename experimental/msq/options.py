from pydantic import BaseModel

from libresvip.model.option_mixins import (
    EnableBreathImportationMixin,
    EnableGenderImportationMixin,
    EnableInstrumentalTrackImportationMixin,
    EnablePitchImportationMixin,
    EnableStrengthImportationMixin,
    EnableVolumeImportationMixin,
)


class InputOptions(
    EnableVolumeImportationMixin,
    EnableBreathImportationMixin,
    EnableGenderImportationMixin,
    EnableStrengthImportationMixin,
    EnableInstrumentalTrackImportationMixin,
    EnablePitchImportationMixin,
    BaseModel,
):
    pass


class OutputOptions(BaseModel):
    pass
