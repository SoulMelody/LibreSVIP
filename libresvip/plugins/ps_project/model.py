from typing import Literal

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
    background_image_name: str | None = Field(None, alias="backgroundImageName")
    bgm_info: PocketSingerBgmMetadata | None = Field(None, alias="bgmInfo")


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
    identifier: int | None = None
    energy_envolope: list[PocketSingerEnvolopeItem] | None = None
    air_envolope: list[PocketSingerEnvolopeItem] | None = None
    tension_envolope: list[PocketSingerEnvolopeItem] | None = None
    falsetto_envolope: list[PocketSingerEnvolopeItem] | None = None


class PocketSingerBrNote(PocketSingerNoteBase):
    type: Literal["br"] = "br"


class PocketSingerNote(PocketSingerNoteBase):
    pitch_bends: list[PocketSingerPitchBend] = Field(default_factory=list, alias="pitchBends")
    consonant_time_head: list[float] | None = None
    phone: list[str] = Field(default_factory=list)
    grapheme_count: int = 1
    grapheme_index: int = 0
    language: PocketSingerLyricsLanguage = PocketSingerLyricsLanguage.CHINESE
    grapheme: str = Field(validation_alias="word")
    pitch: int
    type: Literal["phone"] = "phone"
    br: bool = False
    sin_wave: PocketSingerSinWave | None = None
    user_pitch: list[PocketSingerPitchBend] | None = None
    consonant_time_tail: list[float] | None = None
    br_note: PocketSingerBrNote | None = Field(None, alias="brNote")
    user_phone: list[str] | None = Field(None, alias="userPhone")
    valid: bool | None = None
    key: str | None = None
    scale: list[int] | None = None
    config: str | None = None
    is_edit_phone: bool | None = Field(None, alias="isEditPhone")


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
    mix_info: str | None = None
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
    build_version: str | None = Field(None, alias="buildVersion")
    platform: str = "iOS"
    user_language: PocketSingerLyricsLanguage | None = Field(None, alias="userLanguage")


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
    origin_duration: float | None = None
    origin_start: int | None = None
    author: str | None = None
    tuner: str | None = None
    song_id: int | None = None
    user_id: int | None = None


class PocketSingerProject(BaseModel):
    notes: list[PocketSingerNote] | None = None
    tracks: list[PocketSingerTrack] = Field(default_factory=list)
    bpm: float | None = None
    bgm_info: PocketSingerBgmInfo = Field(default_factory=PocketSingerBgmInfo)
    debug_info: PocketSingerDebugInfo = Field(default_factory=PocketSingerDebugInfo)
    version: int = 3
    timestamp: int | None = None
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
