from pydantic import BaseModel, Field

from libresvip.model.option_mixins import (
    EnableInstrumentalTrackImportationMixin,
    EnablePitchImportationMixin,
)
from libresvip.utils.translation import gettext_lazy as _


class InputOptions(
    EnableInstrumentalTrackImportationMixin,
    EnablePitchImportationMixin,
    BaseModel,
):
    pass


class OutputOptions(BaseModel):
    pretty_xml: bool = Field(
        True,
        title=_("Pretty XML"),
        description=_("Whether to output pretty XML"),
    )
