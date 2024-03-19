from pydantic import BaseModel

from libresvip.model.option_mixins import (
    EnableInstrumentalTrackImportationMixin,
    EnablePitchImportationMixin,
    EnableVibratoImportationMixin,
)


class InputOptions(
    EnableInstrumentalTrackImportationMixin,
    EnablePitchImportationMixin,
    EnableVibratoImportationMixin,
    BaseModel,
):
    pass


class OutputOptions(BaseModel):
    pass
