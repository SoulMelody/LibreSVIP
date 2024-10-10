import enum
from typing import Literal, Optional, Union

from pydantic import (
    Field,
    RootModel,
    SerializationInfo,
    ValidationInfo,
    field_serializer,
    field_validator,
)

from libresvip.model.base import BaseModel


class GlideStyle(enum.Enum):
    NONE = "none"
    UP = "up"
    DOWN = "down"


class DsItem(BaseModel):
    text: list[str]
    ph_seq: list[str]
    note_seq: list[str]
    note_dur: Optional[list[float]] = None
    note_dur_seq: Optional[list[float]] = None
    note_slur: Optional[list[int]] = None
    note_glide: Optional[list[GlideStyle]] = None
    is_slur_seq: Optional[list[int]] = None
    ph_dur: Optional[list[float]] = None
    ph_num: Optional[list[int]] = None
    f0_timestep: Optional[float] = None
    f0_seq: Optional[Union[str, list[float]]] = None
    input_type: Optional[Literal["phoneme"]] = None
    offset: Union[str, float]
    seed: Optional[int] = None
    spk_mix: Optional[dict[str, list[float]]] = None
    spk_mix_timestep: Optional[float] = None
    gender: Optional[list[float]] = None
    gender_timestep: Optional[float] = None
    velocity: Optional[list[float]] = None
    velocity_timestep: Optional[float] = None

    @field_validator("text", "note_seq", "ph_seq", mode="before")
    @classmethod
    def _validate_str_list(cls, value: Optional[str], _info: ValidationInfo) -> Optional[list[str]]:
        return None if value is None else value.split()

    @field_validator("note_glide", mode="before")
    @classmethod
    def _validate_glide_list(
        cls, value: Optional[str], _info: ValidationInfo
    ) -> Optional[list[GlideStyle]]:
        return None if value is None else [GlideStyle(x) for x in value.split()]

    @field_validator(
        "f0_seq",
        "ph_dur",
        "note_dur",
        "note_dur_seq",
        "gender",
        "velocity",
        mode="before",
    )
    @classmethod
    def _validate_float_list(
        cls, value: Optional[str], _info: ValidationInfo
    ) -> Optional[list[float]]:
        return None if value is None else [float(x) for x in value.split()]

    @field_validator("is_slur_seq", "note_slur", "ph_num", mode="before")
    @classmethod
    def _validate_int_list(cls, value: Optional[str], _info: ValidationInfo) -> Optional[list[int]]:
        return None if value is None else [int(x) for x in value.split()]

    @field_serializer(
        "f0_seq",
        "ph_num",
        "ph_dur",
        "note_slur",
        "note_dur",
        "note_dur_seq",
        "is_slur_seq",
        "text",
        "note_seq",
        "ph_seq",
        "gender",
        "velocity",
        when_used="json-unless-none",
    )
    @classmethod
    def _serialize_list(cls, value: list[Union[str, int, float]], _info: SerializationInfo) -> str:
        return " ".join(str(x) for x in value)

    @field_serializer(
        "note_glide",
        when_used="json-unless-none",
    )
    @classmethod
    def _serialize_glide(cls, value: list[GlideStyle], _info: SerializationInfo) -> str:
        return " ".join(x.value for x in value)

    @field_validator("spk_mix", mode="before")
    @classmethod
    def _validate_nested_dict(
        cls, values: Optional[dict[str, str]], _info: ValidationInfo
    ) -> Optional[dict[str, list[float]]]:
        if values is None:
            return None

        return {key: [float(x) for x in value.split()] for key, value in values.items()}

    @field_serializer("spk_mix", when_used="json-unless-none")
    @classmethod
    def _serialize_nested_dict(
        cls, value: dict[str, list[float]], _info: SerializationInfo
    ) -> dict[str, str]:
        return {key: " ".join(str(x) for x in value[key]) for key in value}


class DsProject(RootModel[list[DsItem]]):
    root: list[DsItem] = Field(default_factory=list)
