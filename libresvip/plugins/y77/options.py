from pydantic import BaseModel

from libresvip.model.option_mixins import (
    EnablePitchImportationMixin,
    SelectSingleTrackMixin,
    StaticTempoMixin,
)


class InputOptions(EnablePitchImportationMixin, BaseModel):
    pass


class OutputOptions(SelectSingleTrackMixin, StaticTempoMixin):
    pass
