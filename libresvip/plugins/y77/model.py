from typing import Union

from pydantic import Field

from libresvip.core.constants import DEFAULT_BPM
from libresvip.model.base import BaseModel


class Y77Note(BaseModel):
    py: str = ""
    length: int = Field(alias="len")
    start: int
    lyric: str
    pitch: int
    pbs: int = 0
    pit: list[Union[int, float]] = Field(default_factory=list)


class Y77Project(BaseModel):
    bpm: float = DEFAULT_BPM
    bars: int = 0
    notes: list[Y77Note] = Field(default_factory=list)
    nnote: int = 0
    bbar: int = 4
    v: int = 10001
    bbeat: int = 4
