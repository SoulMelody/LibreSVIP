from typing import Optional

from pydantic import Field

from libresvip.model.base import BaseModel


class VogenNote(BaseModel):
    pitch: Optional[int] = None
    lyric: Optional[str] = None
    rom: Optional[str] = None
    on: Optional[int] = None
    dur: Optional[int] = None


class VogenTrack(BaseModel):
    name: Optional[str] = None
    singer_id: Optional[str] = Field(None, alias="singerId")
    rom_scheme: Optional[str] = Field("", alias="romScheme")
    notes: list[VogenNote] = Field(default_factory=list)


class VogenProject(BaseModel):
    time_sig0: str = Field(alias="timeSig0")
    bpm0: float
    accom_offset: Optional[int] = Field(0, alias="accomOffset")
    utts: list[VogenTrack] = Field(default_factory=list)
