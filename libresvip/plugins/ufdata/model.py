from typing import Optional

from pydantic import Field

from libresvip.model.base import BaseModel


class UFNotes(BaseModel):
    key: int
    tick_on: int = Field(alias="tickOn")
    tick_off: int = Field(alias="tickOff")
    lyric: str


class UFPitch(BaseModel):
    ticks: list[int] = Field(default_factory=list)
    values: list[Optional[float]] = Field(default_factory=list)
    is_absolute: bool = Field(alias="isAbsolute")


class UFTempos(BaseModel):
    tick_position: int = Field(alias="tickPosition")
    bpm: float


class UFTimeSignatures(BaseModel):
    measure_position: int = Field(alias="measurePosition")
    numerator: int = 4
    denominator: int = 4


class UFTracks(BaseModel):
    name: str
    notes: list[UFNotes] = Field(default_factory=list)
    pitch: Optional[UFPitch] = None


class UFProject(BaseModel):
    name: str = "export"
    tracks: list[UFTracks] = Field(default_factory=list)
    time_signatures: list[UFTimeSignatures] = Field(default_factory=list, alias="timeSignatures")
    tempos: list[UFTempos] = Field(default_factory=list)
    measure_prefix: int = Field(alias="measurePrefix")


class UFData(BaseModel):
    format_version: int = Field(1, alias="formatVersion")
    project: UFProject
