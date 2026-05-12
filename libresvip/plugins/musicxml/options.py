from pydantic import BaseModel, Field

from libresvip.utils.translation import gettext_lazy as _


class InputOptions(BaseModel):
    import_tempo: bool = Field(default=True, title=_("Import tempo changes"))
    import_dynamics: bool = Field(default=True, title=_("Import dynamics as volume curve"))
    apply_fermata_stretch: bool = Field(
        default=True, title=_("Extend fermata-bearing notes (matches MuseScore playback)")
    )


class OutputOptions(BaseModel):
    pass
