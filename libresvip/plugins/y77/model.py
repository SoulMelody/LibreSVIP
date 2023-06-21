from typing import Optional, Union

from pydantic import Field

from libresvip.model.base import BaseModel


class Y77Note(BaseModel):
    py: Optional[str]
    len: Optional[int]
    start: Optional[int]
    lyric: Optional[str]
    pitch: Optional[int]
    pbs: Optional[int] = 0
    pit: list[Union[int, float]] = Field(default_factory=list)


class Y77Project(BaseModel):
    bars: Optional[int]
    notes: list[Y77Note] = Field(default_factory=list)
    nnote: Optional[int] = None
    bpm: Optional[float] = 100.0
    bbar: Optional[int]
    v: Optional[int] = 10001
    bbeat: Optional[int]
