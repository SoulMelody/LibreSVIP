from pydantic import BaseModel, Field

from libresvip.model.option_mixins import (
    EnableInstrumentalTrackImportationMixin,
    EnablePitchImportationMixin,
)


class InputOptions(EnableInstrumentalTrackImportationMixin, EnablePitchImportationMixin, BaseModel):
    breath_lyrics: str = Field(
        "Asp AP",
        title="Breath lyrics",
        description="Special lyrics that will be recognized as breath notes only when immediately followed by a regular note, each separated by a space",
    )
    silence_lyrics: str = Field(
        "R SP",
        title="Silence lyrics",
        description="Special lyrics that will be ignored, each separated by a space",
    )


class OutputOptions(BaseModel):
    pass
