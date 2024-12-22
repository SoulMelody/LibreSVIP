from typing import Optional

from pydantic import Field

from libresvip.model.base import BaseModel


class PocketSingerBgmMetadata(BaseModel):
    bar_beat_count: int = Field(alias="barBeatCount")
    beat_segment_count: int = Field(alias="beatSegmentCount")
    bgm_description: str = Field(alias="bgmDescription")
    bpm: float
    display_name: str = Field(alias="displayName")
    file_md5: str = Field(alias="fileMD5")
    file_name: str = Field(alias="fileName")
    file_type: str = Field(alias="fileType")
    first_beat_offset: float = Field(alias="firstBeatOffset")


class PocketSingerMetadata(BaseModel):
    ace_file_name: str = Field(alias="aceFileName")
    background_image_name: Optional[str] = Field(None, alias="backgroundImageName")
    bgm_info: Optional[PocketSingerBgmMetadata] = Field(None, alias="bgmInfo")


class PocketSingerPitchBend(BaseModel):
    pitch: float
    time: float


class PocketSingerEnvolopeItem(BaseModel):
    envolope: float
    time: float


class PocketSingerSinWave(BaseModel):
    release_len: float
    freq: float
    attack_vol: float
    attack_len: float
    amp: float
    start_pos: float
    release_vol: int


class PocketSingerNoteBase(BaseModel):
    start_time: float
    end_time: float
    type: str
    identifier: int
    energy_envolope: Optional[list[PocketSingerEnvolopeItem]] = None
    air_envolope: Optional[list[PocketSingerEnvolopeItem]] = None
    tension_envolope: Optional[list[PocketSingerEnvolopeItem]] = None
    falsetto_envolope: Optional[list[PocketSingerEnvolopeItem]] = None


class PocketSingerBrNote(PocketSingerNoteBase):
    type: str = "br"


class PocketSingerNote(PocketSingerNoteBase):
    pitch_bends: list[PocketSingerPitchBend] = Field(alias="pitchBends")
    consonant_time_head: Optional[list[float]] = None
    phone: list[str]
    grapheme_count: int
    grapheme_index: int
    language: str
    grapheme: str
    pitch: int
    type: str = "phone"
    br: bool = False
    sin_wave: Optional[PocketSingerSinWave] = None
    user_pitch: Optional[list[PocketSingerPitchBend]] = None
    consonant_time_tail: Optional[list[float]] = None
    br_note: Optional[PocketSingerBrNote] = Field(None, alias="brNote")
    user_phone: Optional[list[str]] = Field(None, alias="userPhone")


class PocketSingerRoleInfo(BaseModel):
    name: str
    role_id: int


class PocketSingerTrack(BaseModel):
    sound_effect: int
    pan: int
    ai_svs_mode: bool = Field(alias="AI_SVS_mode")
    lyric: str
    solo: bool
    notes: list[PocketSingerNote]
    language: str
    mix_info: str
    br_notes: list[PocketSingerBrNote]
    role_info: PocketSingerRoleInfo
    mute: bool
    front: bool
    singer_volume: float


class PocketSingerBgmTrack(BaseModel):
    end_time: float
    file_md5: str
    file_name: str
    file_type: str
    position: float
    start_time: float


class PocketSingerBgmInfo(BaseModel):
    tracks: list[PocketSingerBgmTrack]
    mute: bool
    bgm_volume: float
    solo: bool


class PocketSingerDebugInfo(BaseModel):
    version: str
    record_type: str = Field(alias="recordType")
    os: str
    device: str
    build_version: str = Field(alias="buildVersion")
    platform: str


class PocketSingerSongInfo(BaseModel):
    start: int
    first_beat_offset: int
    scale: list[int]
    origin_duration: int
    key: str
    segment_of_beat: int
    operate_scale: list[int] = Field(alias="operateScale")
    bpm: float
    duration: float
    beat_of_bar: int
    name: str
    origin_start: int
    author: str
    song_id: Optional[int] = None
    user_id: Optional[int] = None


class PocketSingerProject(BaseModel):
    tracks: list[PocketSingerTrack]
    bpm: float
    bgm_info: PocketSingerBgmInfo
    debug_info: PocketSingerDebugInfo
    version: int
    timestamp: int
    song_info: PocketSingerSongInfo
