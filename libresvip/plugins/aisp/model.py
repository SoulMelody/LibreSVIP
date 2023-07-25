from typing import Optional, Union

from pydantic import (
    Field,
    SerializationInfo,
    ValidationInfo,
    computed_field,
    field_serializer,
    field_validator,
)

from libresvip.model.base import BaseModel


class AISNote(BaseModel):
    start: Optional[int] = Field(alias="s")
    length: Optional[int] = Field(alias="l")
    m: Optional[int] = None
    lyric: Optional[str] = Field(alias="ly")
    pinyin: Optional[str] = Field(alias="py")
    vel: Optional[int] = None
    tri: Optional[bool] = None
    pit: Optional[list[float]] = None

    @field_validator("pit", mode="before")
    @classmethod
    def validate_pit(
        cls, value: Union[str, list[Union[float, str]]], _info: ValidationInfo
    ) -> Optional[list[float]]:
        if value is None:
            return None
        if isinstance(value, str):
            value = value.split()
        pit_list = []
        for x in value:
            if isinstance(x, str) and "0x" in x:
                pit_list.extend([0] * int(x[2:]))
            elif isinstance(x, str):
                pit_list.append(float(x))
            else:
                pit_list.append(x)
        return pit_list

    @field_serializer("pit", when_used="json-unless-none")
    @classmethod
    def serialize_pit(
        cls, value: Optional[list[float]], _info: SerializationInfo
    ) -> str:
        if value is None:
            return ""
        pit_str = ""
        i = 0
        s0 = None
        e0 = None
        while i < len(value):
            if s0 is None and value[i] == 0:
                s0 = i
                while (
                    e0 is None
                    and value[i] == 0
                    and (value[i + 1] != 0 or i + 1 >= len(value))
                ):
                    e0 = i
                    pit_str += "0x%d " % ((e0 - s0) + 1) if e0 > s0 else "0 "
                    i += 1
                    s0 = None
                    e0 = None
            if value[i] != 0:
                pit_str += f"{round(value[i], 2)} "
            i += 1
        return pit_str.strip()


class AISPattern(BaseModel):
    uid: Optional[int] = None
    start: Optional[int] = Field(alias="s")
    length: Optional[int] = Field(alias="l")
    notes: list[AISNote] = Field(default_factory=list, alias="n")


class AISTrack(BaseModel):
    i: Optional[int] = None
    t: Optional[int] = None
    solo: Optional[bool] = Field(alias="s")
    mute: Optional[bool] = Field(alias="m")
    volume: Optional[int] = Field(alias="v")
    name: Optional[str] = Field(alias="n")
    im: list[AISPattern] = Field(default_factory=list)
    sn: Optional[str] = None
    se: Optional[str] = None
    sh: Optional[str] = None


class AISTimeSignature(BaseModel):
    beat_zi: Optional[int] = None
    beat_mu: Optional[int] = None
    start_bar: Optional[int] = None

    @computed_field(alias="str")
    def str_value(self) -> str:
        return f"{self.beat_zi}/{self.beat_mu}"


class AISTempo(BaseModel):
    tempo_float: Optional[float] = None
    start_128: Optional[int] = None
    start_bar: Optional[int] = None
    start_beat_in_bar: Optional[int] = None


class AISProjectBody(BaseModel):
    num_track: Optional[int] = None
    tracks: list[AISTrack] = Field(default_factory=list)


class AISProjectHead(BaseModel):
    tempo: list[AISTempo] = Field(default_factory=list)
    signature: list[AISTimeSignature] = Field(default_factory=list)
    time: Optional[int] = None
    flags: Optional[int] = None
    flage: Optional[int] = None
    bar: Optional[int] = None
