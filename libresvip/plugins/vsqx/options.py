from pydantic import BaseModel, Field

from libresvip.model.option_mixins import (
    EnableInstrumentalTrackImportationMixin,
    EnablePitchImportationMixin,
)

from .enums import VocaloidLanguage, VsqxVersion


class InputOptions(EnableInstrumentalTrackImportationMixin, EnablePitchImportationMixin, BaseModel):
    pass


class OutputOptions(BaseModel):
    vsqx_version: VsqxVersion = Field(VsqxVersion.VSQ4, title="VSQX Version")
    pretty_xml: bool = Field(True, title="Pretty XML", description="Whether to output pretty XML")
    default_lang_id: VocaloidLanguage = Field(
        VocaloidLanguage.SIMPLIFIED_CHINESE,
        title="Default language",
        description="Default language id of voicebank and notes",
    )
    default_comp_id: str = Field(
        "BETDB8W6KWZPYEB9",
        title="Default Comp ID",
        description="Default comp_id of voicebank",
    )
    default_singer_name: str = Field(
        "Tianyi_CHN",
        title="Default Singer Name",
        description="Default singer name of voicebank",
    )
