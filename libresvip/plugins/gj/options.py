from pydantic import BaseModel, Field

from libresvip.model.option_mixins import (
    EnableInstrumentalTrackImportationMixin,
    EnablePitchImportationMixin,
    EnableVolumeImportationMixin,
)


class InputOptions(
    EnableInstrumentalTrackImportationMixin,
    EnablePitchImportationMixin,
    EnableVolumeImportationMixin,
    BaseModel,
):
    pass


class OutputOptions(BaseModel):
    down_sample: int = Field(
        default=32,
        title="Average sampling interval for the volume parameter",
        description="The unit is Tick. The larger the value, the smoother the editor; the smaller the value, the more accurate the volume parameter.",
    )
    singer: str = Field(
        default="扇宝",
        title="Default singer",
    )
