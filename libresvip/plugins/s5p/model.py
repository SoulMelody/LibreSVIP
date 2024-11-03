from itertools import chain
from typing import NamedTuple, Optional

from more_itertools import batched
from pydantic import (
    Field,
    FieldSerializationInfo,
    RootModel,
    ValidationInfo,
    field_serializer,
    field_validator,
)

from libresvip.core.constants import DEFAULT_BPM, DEFAULT_PHONEME
from libresvip.model.base import BaseModel
from libresvip.model.point import PointList
from libresvip.utils.audio import audio_path_validator


class S5pPoint(NamedTuple):
    offset: float
    value: float


class S5pPoints(PointList[S5pPoint], RootModel[list[S5pPoint]]):
    root: list[S5pPoint] = Field(default_factory=list)


class S5pMeterItem(BaseModel):
    measure: int = 0
    beat_per_measure: int = Field(4, alias="beatPerMeasure")
    beat_granularity: int = Field(4, alias="beatGranularity")


class S5pTempoItem(BaseModel):
    position: int
    beat_per_minute: float = Field(DEFAULT_BPM, alias="beatPerMinute")


class S5pDbDefaults(BaseModel):
    lyric: Optional[str] = DEFAULT_PHONEME
    breathiness: Optional[float] = 0.0
    gender: Optional[float] = 0.0
    tension: Optional[float] = 0.0
    d_f0_vbr: float = Field(0.025, alias="dF0Vbr")
    p_f0_vbr: float = Field(0.0, alias="pF0Vbr")
    t_f0_vbr_left: float = Field(0.15, alias="tF0VbrLeft")
    t_f0_vbr_right: float = Field(0.15, alias="tF0VbrRight")
    t_f0_vbr_start: float = Field(0.25, alias="tF0VbrStart")
    f_f0_vbr: float = Field(5.5, alias="fF0Vbr")
    t_f0_left: float = Field(0.07, alias="tF0Left")
    t_f0_right: float = Field(0.07, alias="tF0Right")
    d_f0_left: float = Field(0.0, alias="dF0Left")
    d_f0_right: float = Field(0.0, alias="dF0Right")
    d_f0_jitter: float = Field(1.0, alias="dF0Jitter")


class S5pNote(BaseModel):
    lyric: str
    onset: int
    duration: int
    comment: str = ""
    pitch: int
    d_f0_vbr: Optional[float] = Field(None, alias="dF0Vbr")
    p_f0_vbr: Optional[float] = Field(None, alias="pF0Vbr")
    t_f0_vbr_left: Optional[float] = Field(None, alias="tF0VbrLeft")
    t_f0_vbr_right: Optional[float] = Field(None, alias="tF0VbrRight")
    t_f0_vbr_start: Optional[float] = Field(None, alias="tF0VbrStart")
    f_f0_vbr: Optional[float] = Field(None, alias="fF0Vbr")
    t_f0_left: Optional[float] = Field(None, alias="tF0Left")
    t_f0_right: Optional[float] = Field(None, alias="tF0Right")
    d_f0_left: Optional[float] = Field(None, alias="dF0Left")
    d_f0_right: Optional[float] = Field(None, alias="dF0Right")
    d_f0_jitter: Optional[float] = Field(None, alias="dF0Jitter")
    t_f0_offset: Optional[float] = Field(None, alias="tF0Offset")
    t_note_offset: Optional[float] = Field(None, alias="tNoteOffset")
    t_syl_onset: Optional[float] = Field(None, alias="tSylOnset")
    t_syl_coda: Optional[float] = Field(None, alias="tSylCoda")
    w_syl_nucleus: Optional[float] = Field(None, alias="wSylNucleus")
    sublib: Optional[str] = None


class S5pTrackMixer(BaseModel):
    gain_decibel: float = Field(0.0, alias="gainDecibel")
    pan: float = 0.0
    muted: bool = False
    solo: bool = False
    engine_on: bool = Field(True, alias="engineOn")
    display: bool = Field(True)


class S5pParameters(BaseModel):
    interval: int = 5512500
    pitch_delta: S5pPoints = Field(default_factory=S5pPoints, alias="pitchDelta")
    vibrato_env: S5pPoints = Field(default_factory=S5pPoints, alias="vibratoEnv")
    loudness: S5pPoints = Field(default_factory=S5pPoints)
    tension: S5pPoints = Field(default_factory=S5pPoints)
    breathiness: S5pPoints = Field(default_factory=S5pPoints)
    voicing: S5pPoints = Field(default_factory=S5pPoints)
    gender: S5pPoints = Field(default_factory=S5pPoints)

    @field_validator(
        "pitch_delta",
        "vibrato_env",
        "loudness",
        "tension",
        "breathiness",
        "voicing",
        "gender",
        mode="before",
    )
    @classmethod
    def validate_points(cls, points: list[float], _info: ValidationInfo) -> S5pPoints:
        if _info.mode == "json":
            return S5pPoints(root=[S5pPoint._make(each) for each in batched(points, 2)])
        return points if isinstance(points, S5pPoints) else S5pPoints(root=points)

    @field_serializer(
        "pitch_delta",
        "vibrato_env",
        "loudness",
        "tension",
        "breathiness",
        "voicing",
        "gender",
        when_used="json",
    )
    def serialize_points(self, points: S5pPoints, _info: FieldSerializationInfo) -> list[float]:
        return list(chain.from_iterable(points.root))


class S5pTrack(BaseModel):
    name: str
    db_name: str = Field("", alias="dbName")
    color: str = "15e879"
    display_order: int = Field(0, alias="displayOrder")
    db_defaults: S5pDbDefaults = Field(default_factory=S5pDbDefaults, alias="dbDefaults")
    notes: list[Optional[S5pNote]] = Field(default_factory=list)
    gs_events: None = Field(None, alias="gsEvents")
    mixer: S5pTrackMixer = Field(default_factory=S5pTrackMixer)
    parameters: S5pParameters = Field(default_factory=S5pParameters)


class S5pInstrumental(BaseModel):
    filename: str = ""
    offset: float = 0.0

    validate_filename = field_validator("filename", mode="before")(audio_path_validator)


class S5pMixer(BaseModel):
    gain_instrumental_decibel: float = Field(0.0, alias="gainInstrumentalDecibel")
    gain_vocal_master_decibel: float = Field(0.0, alias="gainVocalMasterDecibel")
    instrumental_muted: bool = Field(False, alias="instrumentalMuted")
    vocal_master_muted: bool = Field(False, alias="vocalMasterMuted")


class S5pProject(BaseModel):
    version: int = 7
    meter: list[S5pMeterItem] = Field(default_factory=list)
    tempo: list[S5pTempoItem] = Field(default_factory=list)
    tracks: list[S5pTrack] = Field(default_factory=list)
    instrumental: S5pInstrumental = Field(default_factory=S5pInstrumental)
    mixer: S5pMixer = Field(default_factory=S5pMixer)
