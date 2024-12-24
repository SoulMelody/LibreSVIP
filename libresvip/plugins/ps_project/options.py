from pydantic import BaseModel

from libresvip.model.option_mixins import (
    EnableInstrumentalTrackImportationMixin,
    EnablePitchImportationMixin,
    ExtractEmbededAudioMixin,
    StaticTempoMixin,
)


class InputOptions(
    EnableInstrumentalTrackImportationMixin,
    EnablePitchImportationMixin,
    ExtractEmbededAudioMixin,
    BaseModel,
):
    pass


class OutputOptions(StaticTempoMixin, BaseModel):
    pass
