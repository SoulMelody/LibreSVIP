from pydantic import BaseModel

from libresvip.model.option_mixins import (
    EnablePitchImportationMixin,
    SelectSingleTrackMixin,
)


class InputOptions(
    EnablePitchImportationMixin,
    BaseModel,
):
    pass


class OutputOptions(SelectSingleTrackMixin, BaseModel):
    pass
