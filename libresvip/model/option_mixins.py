import abc

from pydantic import BaseModel, Field


class EnablePitchImportationMixin(BaseModel, abc.ABC):
    import_pitch: bool = Field(False, title="Import pitch curve")


class EnableVolumeImportationMixin(BaseModel, abc.ABC):
    import_volume: bool = Field(False, title="Import dynamics curve")


class EnableBreathImportationMixin(BaseModel, abc.ABC):
    import_breath: bool = Field(False, title="Import breath curve")


class EnableGenderImportationMixin(BaseModel, abc.ABC):
    import_gender: bool = Field(False, title="Import gender curve")


class EnableStrengthImportationMixin(BaseModel, abc.ABC):
    import_strength: bool = Field(False, title="Import strength curve")
