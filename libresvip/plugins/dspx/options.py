from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field, create_model

from libresvip.model.option_mixins import EnablePitchImportationMixin
from libresvip.utils.translation import gettext_lazy as _


class PitchImportMode(Enum):
    _value_: Annotated[
        str,
        create_model(
            "PitchImportMode",
            __module__="libresvip.plugins.dspx.options",
            EDITED_AND_ORIGINAL=(str, Field(title=_("Edited and original pitch"))),
            EDITED_ONLY=(str, Field(title=_("Edited pitch only"))),
        ),
    ]
    EDITED_AND_ORIGINAL = "edited-and-original"
    EDITED_ONLY = "edited-only"


class VibratoImportMode(Enum):
    _value_: Annotated[
        str,
        create_model(
            "VibratoImportMode",
            __module__="libresvip.plugins.dspx.options",
            NONE=(str, Field(title=_("Do not import vibrato"))),
            PRESERVE=(str, Field(title=_("Preserve vibrato information on notes"))),
            BAKE_TO_PITCH=(str, Field(title=_("Bake vibrato into the pitch curve"))),
        ),
    ]
    NONE = "none"
    PRESERVE = "preserve"
    BAKE_TO_PITCH = "bake-to-pitch"


class InputOptions(EnablePitchImportationMixin, BaseModel):
    pitch_import_mode: PitchImportMode = Field(
        default=PitchImportMode.EDITED_AND_ORIGINAL,
        title=_("Pitch import mode"),
    )
    import_tone_shift: bool = Field(
        default=True,
        title=_("Bake tone shift into the pitch curve"),
    )
    vibrato_import_mode: VibratoImportMode = Field(
        default=VibratoImportMode.PRESERVE,
        title=_("Vibrato import mode"),
    )


class OutputOptions(BaseModel):
    export_pitch: bool = Field(
        default=True,
        title=_("Export pitch curve"),
    )
    preserve_vibrato: bool = Field(
        default=True,
        title=_("Preserve vibrato"),
    )

