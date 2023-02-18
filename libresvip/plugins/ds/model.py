from typing import Any, List

from libresvip.model.base import BaseModel


class DsItem(BaseModel):
    text: str
    ph_seq: str
    note_seq: str
    note_dur_seq: str
    is_slur_seq: str
    ph_dur: Any
    f0_timestep: str
    f0_seq: str
    input_type: str
    offset: float


class DsProject(BaseModel):
    __root__: List[DsItem]
