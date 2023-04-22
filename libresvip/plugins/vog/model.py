from typing import Optional

from pydantic import Field

from libresvip.model.base import BaseModel


class VogenNote(BaseModel):
    pitch: Optional[int]
    lyric: Optional[str]
    rom: Optional[str]
    on: Optional[int]
    dur: Optional[int]


class VogenTrack(BaseModel):
    name: Optional[str]
    singer_id: Optional[str] = Field(alias="singerId")
    rom_scheme: Optional[str] = Field("", alias="romScheme")
    notes: list[VogenNote] = Field(default_factory=list)


class VogenProject(BaseModel):
    time_sig0: Optional[str] = Field(alias="timeSig0")
    bpm0: Optional[float]
    accom_offset: Optional[int] = Field(0, alias="accomOffset")
    utts: list[VogenTrack] = Field(default_factory=list)
