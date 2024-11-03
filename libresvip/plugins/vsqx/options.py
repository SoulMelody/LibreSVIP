from pydantic import BaseModel, Field

from libresvip.model.option_mixins import (
    EnableInstrumentalTrackImportationMixin,
    EnablePitchImportationMixin,
)
from libresvip.utils.translation import gettext_lazy as _

from .enums import VocaloidLanguage, VsqxVersion


class InputOptions(
    EnableInstrumentalTrackImportationMixin,
    EnablePitchImportationMixin,
    BaseModel,
):
    combine_syllables: bool = Field(
        False,
        title=_("Combine syllables"),
        description=_("Combine multisyllabic lyrics into single words"),
    )


class OutputOptions(BaseModel):
    vsqx_version: VsqxVersion = Field(VsqxVersion.VSQ4, title=_("VSQX Version"))
    pretty_xml: bool = Field(
        True,
        title=_("Pretty XML"),
        description=_("Whether to output pretty XML"),
    )
    default_lang_id: VocaloidLanguage = Field(
        VocaloidLanguage.SIMPLIFIED_CHINESE,
        title=_("Default language"),
        description=_("Default language id of voicebank and notes"),
    )
    default_comp_id: str = Field(
        "BETDB8W6KWZPYEB9",
        title=_("Default Comp ID"),
        description=_("Default comp_id of voicebank"),
    )
    default_singer_name: str = Field(
        "Tianyi_CHN",
        title=_("Default Singer Name"),
        description=_("Default singer name of voicebank"),
    )
