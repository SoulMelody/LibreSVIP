from typing import Any, Dict, List, Literal, Optional, Union

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
    text: SpaceSeparatedString
    ph_seq: SpaceSeparatedString
    note_seq: SpaceSeparatedString
    note_dur_seq: SpaceSeparatedFloat
    is_slur_seq: SpaceSeparatedInt
    ph_dur: SpaceSeparatedFloat
    f0_timestep: FloatString
    f0_seq: SpaceSeparatedFloat
    input_type: Literal["phoneme"]
    offset: float
    spk_mix: Optional[Dict[str, SpaceSeparatedFloat]]
    spk_mix_timestep: Optional[float]
    gender: Optional[Dict[str, SpaceSeparatedFloat]]
    gender_timestep: Optional[float]


class DsProject(BaseModel):
    __root__: List[DsItem]
