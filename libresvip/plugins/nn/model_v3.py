from pydantic import Field

from libresvip.model.base import BaseModel


class NoteDictListItem(BaseModel):
    vib_rat: int = Field(alias="VIB_rat")
    vib_len: int = Field(alias="VIB_len")
    start_64note: int
    pbs: int = Field(alias="PBS")
    cle: float = Field(alias="CLE")
    vib_dep: int = Field(alias="VIB_dep")
    lyric: str
    len_64note: int
    vel: float = Field(alias="VEL")
    dyn_list: list[int] = Field(alias="DYN_list")
    id_value: int = Field(alias="id")
    row: int
    is_triple: bool
    pinyin: str
    pit_list: list[int] = Field(alias="PIT_list")


class TrackDictListItem(BaseModel):
    character_path: str
    note_dict_list: list[NoteDictListItem]
    is_mute: bool
    volume: float
    inf_path: str
    is_solo: bool
    num_note: int
    index: int
    voice_path: str
    readme_path: str
    name: str
    head_path: str
    type_: int = Field(alias="type")


class Niao3Project(BaseModel):
    beat_per_bar: int
    bpm_float: float
    num_bar: int
    track_dict_list: list[TrackDictListItem]
    num_track: int
    base_beat: int
