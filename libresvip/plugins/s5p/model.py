from itertools import chain
from typing import List, NamedTuple, Optional

from more_itertools import chunked
from pydantic import Field, validator

from libresvip.core.constants import DEFAULT_BPM, DEFAULT_PHONEME
from libresvip.model.base import BaseModel
from libresvip.model.point import PointList


class S5pPoint(NamedTuple):
    offset: int
    value: float


class S5pPoints(PointList[S5pPoint]):
    def _iter(
        self,
        **kwargs,
    ):
        for key, value in super()._iter(**kwargs):
            if key == "__root__" and kwargs.get("to_dict", False):
                yield key, list(chain.from_iterable(getattr(self, key)))
            else:
                yield key, value


class S5pMeterItem(BaseModel):
    measure: int = 0
    beat_per_measure: int = Field(4, alias="beatPerMeasure")
    beat_granularity: int = Field(4, alias="beatGranularity")


class S5pTempoItem(BaseModel):
    position: int
    beat_per_minute: float = Field(DEFAULT_BPM, alias="beatPerMinute")


class S5pDbDefaults(BaseModel):
    lyric: Optional[str] = DEFAULT_PHONEME
    breathiness: Optional[float]
    d_f0_vbr: Optional[float] = Field(alias="dF0Vbr")
    d_f0_jitter: Optional[float] = Field(alias="dF0Jitter")
    t_f0_vbr_start: Optional[float] = Field(alias="tF0VbrStart")
    gender: Optional[float]
    tension: Optional[float]


class S5pNote(BaseModel):
    onset: int
    duration: int
    lyric: str
    comment: str = ""
    pitch: int
    d_f0_vbr: Optional[float] = Field(alias="dF0Vbr")
    d_f0_jitter: Optional[float] = Field(alias="dF0Jitter")
    p_f0_vbr: Optional[float] = Field(alias="pF0Vbr")
    t_f0_vbr_left: Optional[float] = Field(alias="tF0VbrLeft")
    t_f0_vbr_right: Optional[float] = Field(alias="tF0VbrRight")
    t_f0_vbr_start: Optional[float] = Field(alias="tF0VbrStart")
    f_f0_vbr: Optional[float] = Field(alias="fF0Vbr")
    t_f0_offset: Optional[float] = Field(alias="tF0Offset")
    t_note_offset: Optional[float] = Field(alias="tNoteOffset")
    t_syl_onset: Optional[float] = Field(alias="tSylOnset")
    t_syl_coda: Optional[float] = Field(alias="tSylCoda")
    w_syl_nucleus: Optional[float] = Field(alias="wSylNucleus")
    sublib: Optional[str] = None


class S5pTrackMixer(BaseModel):
    gain_decibel: float = Field(..., alias="gainDecibel")
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

    @validator(
        "pitch_delta",
        "vibrato_env",
        "loudness",
        "tension",
        "breathiness",
        "voicing",
        "gender",
        pre=True,
    )
    def load_points(cls, points):
        if not isinstance(points, S5pPoints):
            return S5pPoints(__root__=[S5pPoint(*each) for each in chunked(points, 2)])
        return points


class S5pTrack(BaseModel):
    name: str
    db_name: str = Field(..., alias="dbName")
    color: str = "15e879"
    display_order: int = Field(..., alias="displayOrder")
    db_defaults: S5pDbDefaults = Field(
        default_factory=S5pDbDefaults, alias="dbDefaults"
    )
    notes: List[S5pNote] = Field(default_factory=list)
    gs_events: None = Field(None, alias="gsEvents")
    mixer: S5pTrackMixer = Field(default_factory=S5pTrackMixer)
    parameters: S5pParameters = Field(default_factory=S5pParameters)


class S5pInstrumental(BaseModel):
    filename: str = ""
    offset: float = 0.0


class S5pMixer(BaseModel):
    gain_instrumental_decibel: float = Field(0.0, alias="gainInstrumentalDecibel")
    gain_vocal_master_decibel: float = Field(0.0, alias="gainVocalMasterDecibel")
    instrumental_muted: bool = Field(False, alias="instrumentalMuted")
    vocal_master_muted: bool = Field(False, alias="vocalMasterMuted")


class S5pProject(BaseModel):
    version: int = 7
    meter: List[S5pMeterItem] = Field(default_factory=list)
    tempo: List[S5pTempoItem] = Field(default_factory=list)
    tracks: List[S5pTrack] = Field(default_factory=list)
    instrumental: S5pInstrumental = Field(default_factory=S5pInstrumental)
    mixer: S5pMixer = Field(default_factory=S5pMixer)
