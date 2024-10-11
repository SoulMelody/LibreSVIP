from pydantic import BaseModel

from libresvip.model.option_mixins import (
    EnableInstrumentalTrackImportationMixin,
    EnablePitchImportationMixin,
)


class InputOptions(
    EnablePitchImportationMixin,
    EnableInstrumentalTrackImportationMixin,
    BaseModel,
):
    pass


class OutputOptions(BaseModel):
    pass
