from typing import List, Optional

from pydantic import Field

from libresvip.model.base import BaseModel


class AISNote(BaseModel):
    start: Optional[int] = Field(alias="s")
    length: Optional[int] = Field(alias="l")
    m: Optional[int]
    lyric: Optional[str] = Field(alias="ly")
    pinyin: Optional[str] = Field(alias="py")
    vel: Optional[int]
    tri: Optional[bool]
    pit: Optional[str]


class AISPattern(BaseModel):
    uid: Optional[int]
    start: Optional[int] = Field(alias="s")
    length: Optional[int] = Field(alias="l")
    notes: List[AISNote] = Field(default_factory=list, alias="n")


class AISTrack(BaseModel):
    i: Optional[int]
    t: Optional[int]
    solo: Optional[bool] = Field(alias="s")
    mute: Optional[bool] = Field(alias="m")
    volume: Optional[int] = Field(alias="v")
    name: Optional[str] = Field(alias="n")
    im: List[AISPattern] = Field(default_factory=list)
    sn: Optional[str]
    se: Optional[str]
    sh: Optional[str]


class AISTimeSignature(BaseModel):

    str_value: Optional[str] = Field(alias="str")
    beat_zi: Optional[int]
    beat_mu: Optional[int]
    start_bar: Optional[int]


class AISTempo(BaseModel):
    tempo_float: Optional[float]
    start_128: Optional[int]
    start_bar: Optional[int]
    start_beat_in_bar: Optional[int]


class AISProjectBody(BaseModel):
    num_track: Optional[int]
    tracks: List[AISTrack] = Field(default_factory=list)


class AISProjectHead(BaseModel):

    tempo: List[AISTempo] = Field(default_factory=list)
    signature: List[AISTimeSignature] = Field(default_factory=list)
    time: Optional[int]
    flags: Optional[int]
    flage: Optional[int]
    bar: Optional[int]
