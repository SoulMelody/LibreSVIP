from pydantic import BaseModel

from libresvip.model.option_mixins import (
    EnableInstrumentalTrackImportationMixin,
    ExtractEmbededAudioMixin,
    StaticTempoMixin,
)


class InputOptions(EnableInstrumentalTrackImportationMixin, ExtractEmbededAudioMixin, BaseModel):
    pass


class OutputOptions(StaticTempoMixin, BaseModel):
    pass
