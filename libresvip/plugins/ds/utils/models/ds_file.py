import enum
from typing import Literal

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
    note_dur: list[float] | None = None
    note_dur_seq: list[float] | None = None
    note_slur: list[int] | None = None
    note_glide: list[GlideStyle] | None = None
    is_slur_seq: list[int] | None = None
    ph_dur: list[float] | None = None
    ph_num: list[int] | None = None
    f0_timestep: float | None = None
    f0_seq: str | list[float] | None = None
    input_type: Literal["phoneme"] | None = None
    offset: str | float
    seed: int | None = None
    spk_mix: dict[str, list[float]] | None = None
    spk_mix_timestep: float | None = None
    gender: list[float] | None = None
    gender_timestep: float | None = None
    velocity: list[float] | None = None
    velocity_timestep: float | None = None

    @field_validator("text", "note_seq", "ph_seq", mode="before")
    @classmethod
    def _validate_str_list(cls, value: str | None, _info: ValidationInfo) -> list[str] | None:
        return None if value is None else value.split()

    @field_validator("note_glide", mode="before")
    @classmethod
    def _validate_glide_list(
        cls, value: str | None, _info: ValidationInfo
    ) -> list[GlideStyle] | None:
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
    def _validate_float_list(cls, value: str | None, _info: ValidationInfo) -> list[float] | None:
        return None if value is None else [float(x) for x in value.split()]

    @field_validator("is_slur_seq", "note_slur", "ph_num", mode="before")
    @classmethod
    def _validate_int_list(cls, value: str | None, _info: ValidationInfo) -> list[int] | None:
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
    def _serialize_list(cls, value: list[str | int | float], _info: SerializationInfo) -> str:
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
        cls, values: dict[str, str] | None, _info: ValidationInfo
    ) -> dict[str, list[float]] | None:
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
