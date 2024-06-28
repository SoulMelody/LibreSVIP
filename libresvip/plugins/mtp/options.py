from gettext import gettext as _

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
        title=_("Default Singer Name"),
        description=_("The default singer name to use for all tracks"),
    )
