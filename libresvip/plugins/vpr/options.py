from pydantic import BaseModel, Field

from libresvip.model.option_mixins import (
    EnableInstrumentalTrackImportationMixin,
    EnablePitchImportationMixin,
    ExtractEmbededAudioMixin,
)
from libresvip.utils.translation import gettext_lazy as _

from .model import VocaloidLanguage


class InputOptions(
    EnableInstrumentalTrackImportationMixin,
    EnablePitchImportationMixin,
    ExtractEmbededAudioMixin,
    BaseModel,
):
    pass


class OutputOptions(BaseModel):
    is_ai_singer: bool = Field(
        False,
        title=_("Is AI Singer"),
        description=_("The default voicebank is AI singer or not"),
    )
    default_lang_id: VocaloidLanguage = Field(
        VocaloidLanguage.SIMPLIFIED_CHINESE,
        title=_("Default language"),
        description=_("Default language id of voicebank and notes"),
    )
    default_comp_id: str = Field(
        "BL8CEAM5N4XN3LFK",
        title=_("Default Comp ID"),
        description=_("Default comp_id of voicebank"),
    )
    default_singer_name: str = Field(
        "Luo_Tianyi_Wan",
        title=_("Default Singer Name"),
        description=_("Default singer name of voicebank"),
    )
