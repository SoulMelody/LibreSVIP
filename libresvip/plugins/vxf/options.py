from pydantic import BaseModel, Field

from libresvip.core.constants import DEFAULT_BPM, TICKS_IN_BEAT
from libresvip.model.option_mixins import EnablePitchImportationMixin
from libresvip.utils.translation import gettext_lazy as _


class InputOptions(EnablePitchImportationMixin, BaseModel):
    default_bpm: float = Field(
        default=DEFAULT_BPM,
        title=_("Default BPM"),
        description=_("Used when no BPM information is found in the MIDI file."),
    )


class OutputOptions(BaseModel):
    ticks_per_beat: int = Field(
        default=TICKS_IN_BEAT,
        title=_("Ticks per beat"),
        description=_(
            "Also known as parts per quarter, ticks per quarter note, the number of pulses per quarter note. This setting should not be changed unless you know what it is."
        ),
    )
