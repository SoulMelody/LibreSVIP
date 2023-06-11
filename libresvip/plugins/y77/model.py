from typing import List, Optional, Union

from pydantic import Field

from libresvip.model.base import BaseModel


class Y77Note(BaseModel):
    py: Optional[str]
    len: Optional[int]
    start: Optional[int]
    lyric: Optional[str]
    pitch: Optional[int]
    pbs: Optional[int] = 0
    pit: List[Union[int, float]] = Field(default_factory=list)


class Y77Project(BaseModel):
    bars: Optional[int]
    notes: List[Y77Note] = Field(default_factory=list)
    nnote: Optional[int]
    bpm: Optional[float] = 100.0
    bbar: Optional[int]
    v: Optional[int] = 10001
    bbeat: Optional[int]
