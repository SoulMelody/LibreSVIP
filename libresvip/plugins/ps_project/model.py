from typing import Literal, Optional

from pydantic import Field, ValidationInfo, model_validator
from typing_extensions import Self

from libresvip.model.base import BaseModel

from .enums import PocketSingerLyricsLanguage


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

    @model_validator(mode="after")
    def extract_audio(self, info: ValidationInfo) -> Self:
        if (
            info.context is not None
            and info.context["extract_audio"]
            and not hasattr(info.context["path"], "protocol")
        ):
            archive_audio_path = f"{self.file_name}.{self.file_type}"
            if not (
                audio_path := (
                    info.context["path"].parent / f"{self.display_name}.{self.file_type}"
                )
            ).exists():
                audio_path.write_bytes(info.context["archive_file"].read(archive_audio_path))
        return self


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
    release_vol: float


class PocketSingerNoteBase(BaseModel):
    start_time: float
    end_time: float
    identifier: Optional[int] = None
    energy_envolope: Optional[list[PocketSingerEnvolopeItem]] = None
    air_envolope: Optional[list[PocketSingerEnvolopeItem]] = None
    tension_envolope: Optional[list[PocketSingerEnvolopeItem]] = None
    falsetto_envolope: Optional[list[PocketSingerEnvolopeItem]] = None


class PocketSingerBrNote(PocketSingerNoteBase):
    type: Literal["br"] = "br"


class PocketSingerNote(PocketSingerNoteBase):
    pitch_bends: list[PocketSingerPitchBend] = Field(default_factory=list, alias="pitchBends")
    consonant_time_head: Optional[list[float]] = None
    phone: list[str] = Field(default_factory=list)
    grapheme_count: int = 1
    grapheme_index: int = 0
    language: PocketSingerLyricsLanguage = PocketSingerLyricsLanguage.CHINESE
    grapheme: str = Field(validation_alias="word")
    pitch: int
    type: Literal["phone"] = "phone"
    br: bool = False
    sin_wave: Optional[PocketSingerSinWave] = None
    user_pitch: Optional[list[PocketSingerPitchBend]] = None
    consonant_time_tail: Optional[list[float]] = None
    br_note: Optional[PocketSingerBrNote] = Field(None, alias="brNote")
    user_phone: Optional[list[str]] = Field(None, alias="userPhone")
    valid: Optional[bool] = None
    key: Optional[str] = None
    scale: Optional[list[int]] = None
    config: Optional[str] = None
    is_edit_phone: Optional[bool] = Field(None, alias="isEditPhone")


class PocketSingerRoleInfo(BaseModel):
    name: str = ""
    role_id: int = 0


class PocketSingerTrack(BaseModel):
    sound_effect: int = 0
    pan: float = 0
    ai_svs_mode: bool = Field(True, alias="AI_SVS_mode")
    lyric: str = ""
    solo: bool = False
    notes: list[PocketSingerNote] = Field(default_factory=list)
    language: PocketSingerLyricsLanguage = PocketSingerLyricsLanguage.CHINESE
    mix_info: Optional[str] = None
    br_notes: list[PocketSingerBrNote] = Field(default_factory=list)
    role_info: PocketSingerRoleInfo = Field(default_factory=PocketSingerRoleInfo)
    mute: bool = False
    front: bool = False
    singer_volume: float = 1


class PocketSingerBgmTrack(BaseModel):
    end_time: float
    file_md5: str
    file_name: str
    file_type: str
    position: float
    start_time: float


class PocketSingerBgmInfo(BaseModel):
    tracks: list[PocketSingerBgmTrack] = Field(default_factory=list)
    mute: bool = False
    bgm_volume: float = 1
    solo: bool = False


class PocketSingerDebugInfo(BaseModel):
    version: str = "1.6.2"
    record_type: str = Field("create", alias="recordType")
    os: str = "16"
    device: str = "iPad8,3"
    build_version: Optional[str] = Field(None, alias="buildVersion")
    platform: str = "iOS"
    user_language: Optional[PocketSingerLyricsLanguage] = Field(None, alias="userLanguage")


class PocketSingerSongInfo(BaseModel):
    start: int
    first_beat_offset: float
    scale: list[int]
    key: str
    segment_of_beat: int
    operate_scale: list[int] = Field(alias="operateScale")
    bpm: float
    duration: float
    beat_of_bar: int
    name: str
    origin_duration: Optional[float] = None
    origin_start: Optional[int] = None
    author: Optional[str] = None
    tuner: Optional[str] = None
    song_id: Optional[int] = None
    user_id: Optional[int] = None


class PocketSingerProject(BaseModel):
    notes: Optional[list[PocketSingerNote]] = None
    tracks: list[PocketSingerTrack] = Field(default_factory=list)
    bpm: Optional[float] = None
    bgm_info: PocketSingerBgmInfo = Field(default_factory=PocketSingerBgmInfo)
    debug_info: PocketSingerDebugInfo = Field(default_factory=PocketSingerDebugInfo)
    version: int = 3
    timestamp: Optional[int] = None
    song_info: PocketSingerSongInfo

    @model_validator(mode="after")
    def migrate_notes(self) -> Self:
        if self.notes is not None:
            self.version = 1
            self.tracks.append(
                PocketSingerTrack(
                    notes=self.notes,
                )
            )
        return self
