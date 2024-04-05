from __future__ import annotations

from enum import Enum
from types import SimpleNamespace
from typing import Annotated, Literal, Union

from pydantic import Field, ValidationInfo, field_validator

from libresvip.model.base import BaseModel
from libresvip.model.option_mixins import (
    EnableBreathImportationMixin,
    EnableGenderImportationMixin,
    EnableInstrumentalTrackImportationMixin,
    EnablePitchImportationMixin,
)

from .model import AcepLyricsLanguage
from .singers import DEFAULT_SINGER


class StrengthMappingOption(Enum):
    BOTH: Annotated[
        str,
        Field(
            title="Both strength and tension",
            description="Map both strength and tension parameters to strength and tension parameters, each with a weight of 50%.",
        ),
    ] = "both"
    ENERGY: Annotated[
        str,
        Field(
            title="Only strength",
            description="Map only strength parameters to strength parameters. Tension parameters will remain unparameterized.",
        ),
    ] = "energy"
    TENSION: Annotated[
        str,
        Field(
            title="Only tension",
            description="Map only tension parameters to tension parameters. Strength parameters will remain unparameterized.",
        ),
    ] = "tension"


NormalizationMethod = SimpleNamespace(
    NONE="none",
    ZSCORE="zscore",
    MINMAX="minmax",
)


class NormalizationArgument(BaseModel):
    normalize_method: Literal["none", "zscore", "minmax"] = NormalizationMethod.NONE
    lower_threshold: float = Field(default=0, ge=0.0, le=10.0)
    upper_threshold: float = Field(default=10, ge=0.0, le=10.0)
    scale: float = Field(default=0, ge=-1.0, le=1.0)
    bias: float = Field(default=0, ge=-1.0, le=1.0)

    @classmethod
    def default_repr(cls) -> str:
        fields = cls.model_fields
        default_strs = [str(field.default) for field in fields.values()]
        return ",".join(default_strs)

    @classmethod
    def from_str(cls, v: str) -> NormalizationArgument:
        fields = cls.model_fields
        try:
            obj = cls(**dict(zip(fields.keys(), v.split(","))))
        except Exception:
            obj = cls()
        return obj

    @property
    def enabled(self) -> bool:
        return self.normalize_method != "none"


class InputOptions(
    EnableBreathImportationMixin,
    EnableGenderImportationMixin,
    EnableInstrumentalTrackImportationMixin,
    EnablePitchImportationMixin,
    BaseModel,
):
    keep_all_pronunciation: bool = Field(
        default=False,
        title="Keep all pronunciation information",
        description="ACE Studio will add pronunciation to all notes. This is a redundant data for most Chinese characters, so by default only modified pronunciation will be kept. When this option is turned on, all pronunciation information will be kept unconditionally, but it may produce a larger file size. When the source file contains non-Chinese singing data, please turn on this option.",
    )
    import_tension: bool = Field(
        default=True,
        title="Import tension envelope",
        description="When turned on, the tension envelope will be mapped to the tension channel of the intermediate model.",
    )
    import_energy: bool = Field(
        default=True,
        title="Import energy envelope",
        description="When turned on, the energy envelope will be mapped to the energy channel of the intermediate model.",
    )
    energy_coefficient: float = Field(
        default=0.5,
        title="Strength-volume mapping coefficient",
        description="Since the strength parameter of ACE Studio has a significant impact on the volume, this option is provided to control the mapping coefficient of the strength envelope. The strength envelope will be multiplied by the value of this option as a whole and then mapped to the volume channel of the intermediate model, and the remaining part will be mapped to the strength channel. This option accepts values in the range of 0~1.0.",
    )
    curve_sample_interval: int = Field(
        default=5,
        title="Interval of curve sampling",
        description="The unit is tick (the length of a quarter note is 480 ticks). By default, the parameter points in the acep file are stored in a very dense manner. Increasing the sampling interval appropriately will not cause much loss of accuracy, but it can get a smaller file size. Setting to 0 or a negative value means keeping the original sampling interval.",
    )
    breath_normalization: NormalizationArgument = Field(
        default_factory=NormalizationArgument,
        title="Breath parameter normalization",
        description="""This option is an advanced option. After enabling this option, the breath parameters will be merged with the breath envelope after being transformed by the normalization. It is recommended to enable this option after fixing all parameters with a fixed brush. This option needs to set 5 values, separated by "," from each other:
(1) Normalization method: none means to turn off this option, zscore means to perform Z-Score normalization on the parameter points, and minmax means to Min-Max normalize the parameter points to the [-1.0, 1.0] interval.
(2) Lower threshold: a real number in the range of 0~10.0, the parameter points lower than this value will not participate in the normalization.
(3) Upper threshold: a real number in the range of 0~10.0, the parameter points higher than this value will not participate in the normalization.
(4) Scaling factor: a real number in the range of -1.0~1.0, the normalized parameter value will be multiplied by this value.
(5) Bias: a real number in the range of -1.0~1.0, the normalized and scaled parameter value will be added to this value.""",
    )
    tension_normalization: NormalizationArgument = Field(
        default_factory=NormalizationArgument,
        title="Tension parameter normalization",
        description="""This option is an advanced option. After enabling this option, the tension parameters will be merged with the tension envelope after being transformed by the normalization. It is recommended to enable this option after fixing all parameters with a fixed brush. This option needs to set 5 values, separated by "," from each other:
(1) Normalization method: none means to turn off this option, zscore means to perform Z-Score normalization on the parameter points, and minmax means to Min-Max normalize the parameter points to the [-1.0, 1.0] interval.
(2) Lower threshold: a real number in the range of 0~10.0, the parameter points lower than this value will not participate in the normalization.
(3) Upper threshold: a real number in the range of 0~10.0, the parameter points higher than this value will not participate in the normalization.
(4) Scaling factor: a real number in the range of -1.0~1.0, the normalized parameter value will be multiplied by this value.
(5) Bias: a real number in the range of -1.0~1.0, the normalized and scaled parameter value will be added to this value.""",
    )
    energy_normalization: NormalizationArgument = Field(
        default_factory=NormalizationArgument,
        title="Energy parameter normalization",
        description="""This option is an advanced option. After enabling this option, the energy parameters will be merged with the energy envelope after being transformed by the normalization. It is recommended to enable this option after fixing all parameters with a fixed brush. This option needs to set 5 values, separated by "," from each other:
(1) Normalization method: none means to turn off this option, zscore means to perform Z-Score normalization on the parameter points, and minmax means to Min-Max normalize the parameter points to the [-1.0, 1.0] interval.
(2) Lower threshold: a real number in the range of 0~10.0, the parameter points lower than this value will not participate in the normalization.
(3) Upper threshold: a real number in the range of 0~10.0, the parameter points higher than this value will not participate in the normalization.
(4) Scaling factor: a real number in the range of -1.0~1.0, the normalized parameter value will be multiplied by this value.
(5) Bias: a real number in the range of -1.0~1.0, the normalized and scaled parameter value will be added to this value.""",
    )

    @field_validator(
        "breath_normalization",
        "tension_normalization",
        "energy_normalization",
        mode="before",
    )
    @classmethod
    def _validate_normalization_argument(
        cls, v: Union[str, dict[str, Union[str, float]]], _info: ValidationInfo
    ) -> NormalizationArgument:
        if isinstance(v, str):
            v = NormalizationArgument.from_str(v).model_dump()
        return v


class OutputOptions(BaseModel):
    singer: str = Field(
        default=DEFAULT_SINGER,
        title="Default singer",
        description="Please input the complete and correct singer name",
    )
    breath: int = Field(
        default=600,
        title="Default breath length (ms)",
        description="This option is used to set the default breath length when the breath mark is converted to a breath parameter. The actual breath length may be less than the default value due to the small gap between notes; some notes may be shortened due to the insertion of breath marks. Setting to 0 or a negative value means ignoring all breath marks.",
    )
    map_strength_info: StrengthMappingOption = Field(
        default=StrengthMappingOption.BOTH,
        title="Map strength and tension parameters to",
        description="ACE Studio has both strength and tension parameters, both of which can affect the strength of the singing. This option is used to set the mapping target of the strength parameter.",
    )
    split_threshold: int = Field(
        default=1,
        title="Threshold for splitting",
        description="When the distance between notes exceeds the set value, they will be split into different segments (patterns) for subsequent editing. The threshold unit is the value of a quarter note, and the default is 1, which means that when the distance between notes exceeds 1 quarter notes (480 ticks), they will be split. If you don't want to split at all, please set this option to 0 or a negative value.",
    )
    lyric_language: AcepLyricsLanguage = Field(
        default=AcepLyricsLanguage.CHINESE,
        title="Lyrics language",
        description="ACE Studio supports three languages of lyrics. This option is used to set the language of lyrics.",
    )
    export_pitch: bool = Field(
        default=True,
        title="Export pitch curve or not",
        description="Warning: when turned on, it may cause consonant issues",
    )
    default_consonant_length: int = Field(
        default=0,
        title="Default consonant length (ticks)",
        description="Set default consonant length for notes if not specified",
    )
