from pydantic import BaseModel

from libresvip.model.option_mixins import (
    EnableInstrumentalTrackImportationMixin,
    EnablePitchImportationMixin,
    ExtractEmbededAudioMixin,
    SelectSingleTrackMixin,
)


class InputOptions(
    EnableInstrumentalTrackImportationMixin,
    EnablePitchImportationMixin,
    ExtractEmbededAudioMixin,
    BaseModel,
):
    pass


class OutputOptions(SelectSingleTrackMixin, BaseModel):
    pass
