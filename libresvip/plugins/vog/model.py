from pydantic import Field

from libresvip.model.base import BaseModel


class VogenNote(BaseModel):
    pitch: int | None = None
    lyric: str | None = None
    rom: str | None = None
    on: int | None = None
    dur: int | None = None


class VogenTrack(BaseModel):
    name: str | None = None
    singer_id: str | None = Field(None, alias="singerId")
    rom_scheme: str | None = Field("", alias="romScheme")
    notes: list[VogenNote] = Field(default_factory=list)


class VogenProject(BaseModel):
    time_sig0: str = Field(alias="timeSig0")
    bpm0: float
    accom_offset: int | None = Field(0, alias="accomOffset")
    utts: list[VogenTrack] = Field(default_factory=list)
