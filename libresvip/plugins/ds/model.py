from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import field_serializer, field_validator, model_serializer, root_validator

from libresvip.model.base import BaseModel


class FloatString(str):
    @classmethod
    def __get_validators__(cls):  # noqa: D105
        def validate(value: Union[str, float]) -> float:
            """Checks whether the value is a float or a string representing a float."""
            if isinstance(value, float):
                return value

            if isinstance(value, str):
                return float(value)

            raise TypeError("Invalid float")

        yield validate


class SpaceSeparatedString(str):
    """Pydantic field type validating space separated strings or lists."""

    _item_type = None

    @classmethod
    def __get_validators__(cls):  # noqa: D105
        def validate(value: Union[str, List[Any]]) -> List[Any]:
            """Checks whether the value is a space separated string or a list."""
            if isinstance(value, list):
                return value

            if isinstance(value, str):
                if cls._item_type is not None:
                    return [cls._item_type(v) for v in value.split()]
                else:
                    return value.split()

            if value is None:
                return []

            raise TypeError("Invalid space separated list")

        yield validate


class SpaceSeparatedInt(SpaceSeparatedString):
    _item_type = int


class SpaceSeparatedFloat(SpaceSeparatedString):
    _item_type = float


class DsItem(BaseModel):
    text: List[str]
    ph_seq: List[str]
    note_seq: List[str]
    note_dur_seq: List[float]
    is_slur_seq: List[int]
    ph_dur: List[float]
    f0_timestep: float
    f0_seq: List[float]
    input_type: Literal["phoneme"]
    offset: float
    seed: Optional[int]
    spk_mix: Optional[Dict[str, List[float]]]
    spk_mix_timestep: Optional[float]
    gender: Optional[Dict[str, List[float]]]
    gender_timestep: Optional[float]

    @field_validator("spk_mix", "gender", mode="before")
    @classmethod
    def _validate_nested_dict(cls, value, _info):
        if value is None:
            return None

        for key in value:
            value[key] = [float(x) for x in value[key]]
        return value

    @field_serializer("spk_mix", "gender")
    @classmethod
    def _serialize_nested_dict(cls, value, _info):
        if value is None:
            return None

        return {key: " ".join(str(x) for x in value[key]) for key in value}


class DsProject(BaseModel):
    root: List[DsItem]

    @root_validator(pre=True)
    @classmethod
    def populate_root(cls, values):
        return {'root': values}

    @model_serializer(mode='wrap')
    def _serialize(self, handler, info):
        data = handler(self)
        return data['root'] if info.mode == 'json' else data

    @classmethod
    def model_modify_json_schema(cls, json_schema):
        return json_schema['properties']['root']

    def _iter(
        self,
        **kwargs,
    ):
        def _convert_value(key, value):
            if isinstance(value, list):
                return " ".join(str(x) for x in value)
            elif isinstance(value, dict):
                return {k: " ".join(str(x) for x in v) for k, v in value.items()}
            elif key == "f0_timestep":
                return str(value)
            else:
                return value

        yield "root", [
            {key: _convert_value(key, value) for key, value in item.items()}
            for item in next(super()._iter(**kwargs))[1]
        ]
