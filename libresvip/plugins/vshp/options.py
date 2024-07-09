from pydantic import BaseModel, Field

from libresvip.utils.translation import gettext_lazy as _


class InputOptions(BaseModel):
    wave_to_singing: bool = Field(True, title=_("Convert wave pattern to singing pattern"))
    use_edited_pitch: bool = Field(True, title=_("Use edited pitch curve"))
    use_edited_dynamics: bool = Field(True, title=_("Use edited dynamics curve"))
    import_dynamics: bool = Field(False, title=_("Import dynamics curve"))
    import_formant: bool = Field(False, title=_("Import formant curve"))
    import_breath: bool = Field(False, title=_("Import breath curve"))
