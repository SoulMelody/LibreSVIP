from typing import Optional, Union

from pydantic import Field

from libresvip.core.constants import DEFAULT_BPM
from libresvip.model.base import BaseModel


class Y77Note(BaseModel):
    py: Optional[str] = None
    length: Optional[int] = Field(alias="len")
    start: Optional[int] = None
    lyric: Optional[str] = None
    pitch: Optional[int] = None
    pbs: Optional[int] = 0
    pit: list[Union[int, float]] = Field(default_factory=list)


class Y77Project(BaseModel):
    bpm: float = DEFAULT_BPM
    bars: Optional[int] = None
    notes: list[Y77Note] = Field(default_factory=list)
    nnote: Optional[int] = None
    bbar: Optional[int] = None
    v: Optional[int] = 10001
    bbeat: Optional[int] = None
