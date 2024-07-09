import abc

from pydantic import BaseModel, Field

from libresvip.core.constants import DEFAULT_BPM
from libresvip.utils.translation import gettext_lazy as _


class EnableInstrumentalTrackImportationMixin(BaseModel, abc.ABC):
    import_instrumental_track: bool = Field(True, title=_("Import instrumental tracks"))


class EnablePitchImportationMixin(BaseModel, abc.ABC):
    import_pitch: bool = Field(True, title=_("Import pitch curve"))


class EnableVolumeImportationMixin(BaseModel, abc.ABC):
    import_volume: bool = Field(True, title=_("Import dynamics envelope"))


class EnableBreathImportationMixin(BaseModel, abc.ABC):
    import_breath: bool = Field(True, title=_("Import breath envelope"))


class EnableGenderImportationMixin(BaseModel, abc.ABC):
    import_gender: bool = Field(True, title=_("Import gender envelope"))


class EnableStrengthImportationMixin(BaseModel, abc.ABC):
    import_strength: bool = Field(True, title=_("Import strength envelope"))


class StaticTempoMixin(BaseModel, abc.ABC):
    tempo: float = Field(
        default=DEFAULT_BPM,
        title=_("Constant tempo"),
        description=_("Use this tempo to reset time axis of projects with dynamic tempos"),
    )


class SelectSingleTrackMixin(BaseModel, abc.ABC):
    track_index: int = Field(
        default=-1,
        title=_("Track index"),
        description=_("Start from 0, -1 means automatic selection"),
    )
