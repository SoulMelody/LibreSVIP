from typing import Self

from pydantic import AliasChoices, Field, field_validator, model_validator

from libresvip.model.base import BaseModel


class AceEnvelopePoint(BaseModel):
    time: float
    envolope: float


class AcePitchBend(BaseModel):
    time: float
    pitch: float


class AceTimedItem(BaseModel):
    start_time: float
    end_time: float
    energy_envolope: list[AceEnvelopePoint] | None = None
    air_envolope: list[AceEnvelopePoint] | None = None
    tension_envolope: list[AceEnvelopePoint] | None = None
    falsetto_envolope: list[AceEnvelopePoint] | None = None


class AceBreathNote(AceTimedItem):
    pinyin: str = "br"


class AceNote(AceTimedItem):
    pitch: int
    word: str = ""
    pinyin: str = ""
    pitch_bends: list[AcePitchBend] = Field(default_factory=list, alias="pitchBends")
    user_pitch: list[AcePitchBend] | None = None
    br: bool = False
    config: str | None = None
    consonant_time_abs: float | None = None
    key: str | None = None
    scale: list[int] | None = None


class AceRoleInfo(BaseModel):
    name: str = ""
    role_id: int = 0


class AceTrack(BaseModel):
    ai_svs_mode: bool = Field(True, alias="AI_SVS_mode")
    br_notes: list[AceBreathNote] = Field(default_factory=list)
    front: bool = False
    lyric: str = ""
    unread_lyric: str = Field("", alias="unReadLyric")
    mix_info: str | None = None
    mute: bool = False
    notes: list[AceNote] = Field(default_factory=list)
    pan: float = 0.0
    role_info: AceRoleInfo = Field(default_factory=AceRoleInfo)
    singer_volume: float = 1.0
    solo: bool = False
    sound_effect: int = 0


class AceBgmTrack(BaseModel):
    bpm: float | None = None
    end_time: float = 0.0
    file_md5: str = ""
    file_name: str = ""
    file_type: str = ""
    position: float = 0.0
    start_time: float = 0.0


class AceBgmInfo(BaseModel):
    tracks: list[AceBgmTrack] = Field(default_factory=list)
    bgm_volume: float = 1.0
    mute: bool = False
    solo: bool = False


class AceSetting(BaseModel):
    bgm_volume: float = 1.0
    sampler_loop: bool = False
    singer_volume: float = 1.0


class AceSongInfo(BaseModel):
    author: str = ""
    beat_of_bar: int = 4
    bpm: float = 120.0
    cover_file: str | None = None
    duration: float = 0.0
    first_beat_offset: float = 0.0
    key: str = "C"
    lyric: str = ""
    name: str = "New Project"
    operate_scale: list[int] | None = Field(None, alias="operateScale")
    pinyin_lyric: str | None = Field(None, alias="pinyinLyric")
    read_lyric: str | None = Field(None, alias="readLyric")
    read_pinyin_lyric: str | None = Field(None, alias="readPinyinLyric")
    scale: list[int] = Field(default_factory=list)
    segment_of_beat: int = 4
    song_id: int = 0
    start: float = 0.0
    unread_lyric: str = Field("", alias="unReadLyric")
    unread_pinyin_lyric: str | None = Field(None, alias="unReadPinyinLyric")
    user_id: int = 0


class AceDebugInfo(BaseModel):
    device: str = ""
    os: str = ""
    platform: str = "android"
    record_type: str = Field("create", alias="recordType")
    version: str = "3.2.5"


class AceProject(BaseModel):
    bgm_info: AceBgmInfo = Field(default_factory=AceBgmInfo)
    br_notes: list[AceBreathNote] = Field(default_factory=list)
    debug_info: AceDebugInfo | None = Field(
        None,
        validation_alias=AliasChoices("debug_info", "debugInfo"),
    )
    notes: list[AceNote] = Field(default_factory=list)
    role_info: AceRoleInfo = Field(default_factory=AceRoleInfo)
    setting: AceSetting = Field(default_factory=AceSetting)
    song_info: AceSongInfo = Field(default_factory=AceSongInfo)
    tracks: list[AceTrack] = Field(default_factory=list)
    version: int = 2

    @field_validator("tracks", mode="before")
    @classmethod
    def normalize_null_tracks(cls, value: object) -> object:
        # Some legacy mobile projects contain an explicit `"tracks": null`.
        return [] if value is None else value

    @model_validator(mode="after")
    def mark_legacy_project_version(self) -> Self:
        if self.notes:
            self.version = 1
        return self

    def singing_tracks(self) -> list[AceTrack]:
        if self.tracks:
            return self.tracks
        if self.notes:
            return [
                AceTrack(
                    br_notes=self.br_notes,
                    notes=self.notes,
                    role_info=self.role_info,
                    singer_volume=self.setting.singer_volume,
                )
            ]
        return []
