from typing import Optional

from pydantic import Field

from libresvip.model.base import BaseModel


class AISNote(BaseModel):
    start: Optional[int] = Field(alias="s")
    length: Optional[int] = Field(alias="l")
    m: Optional[int] = None
    lyric: Optional[str] = Field(alias="ly")
    pinyin: Optional[str] = Field(alias="py")
    vel: Optional[int] = None
    tri: Optional[bool] = None
    pit: Optional[str] = None


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
    str_value: Optional[str] = Field(alias="str")
    beat_zi: Optional[int] = None
    beat_mu: Optional[int] = None
    start_bar: Optional[int] = None


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
