from pydantic import BaseModel, Field

from libresvip.model.option_mixins import (
    EnableInstrumentalTrackImportationMixin,
    EnablePitchImportationMixin,
)


class InputOptions(EnableInstrumentalTrackImportationMixin, EnablePitchImportationMixin, BaseModel):
    pass


class OutputOptions(BaseModel):
    default_singer_name: str = Field(
        "嫣汐",
        title="Default Singer Name",
        description="The default singer name to use for all tracks",
    )
