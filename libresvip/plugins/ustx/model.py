from types import SimpleNamespace
from typing import Annotated, Dict, List, Literal, Optional, Union

from pydantic import Field

from libresvip.model.base import BaseModel

ParamType = SimpleNamespace(
    CURVE="Curve",
    NUMERICAL="Numerical",
    OPTIONS="Options",
)


class BaseExpression(BaseModel):
    name: str
    abbr: str
    min_: int = Field(alias="min")
    max_: int = Field(alias="max")
    default_value: int
    is_flag: bool


class CurveExpression(BaseExpression):
    type_: Literal["Curve"] = Field(ParamType.CURVE, alias="type")
    flag: str


class NumericalExpression(BaseExpression):
    type_: Literal["Numerical"] = Field(ParamType.NUMERICAL, alias="type")
    flag: str


class OptionsExpression(BaseExpression):
    type_: Literal["Options"] = Field(ParamType.OPTIONS, alias="type")
    options: List[str] = Field(default_factory=list)


UExpressionDescriptor = Annotated[
    Union[CurveExpression, NumericalExpression, OptionsExpression],
    Field(discriminator='type_')
]


class UCurve(BaseModel):
    xs: List[int] = Field(default_factory=list)
    ys: List[int] = Field(default_factory=list)
    abbr: Optional[str]


class PitchData(BaseModel):
    x: Optional[int]
    y: Optional[int]
    shape: Optional[str]


class UTempo(BaseModel):
    position: Optional[int]
    bpm: Optional[int]


class UTimeSignature(BaseModel):
    bar_position: Optional[int]
    beat_per_bar: Optional[int]
    beat_unit: Optional[int]


class URendererSettings(BaseModel):
    renderer: Optional[str]
    resampler: Optional[str]
    wavtool: Optional[str]


class UTrack(BaseModel):
    singer: Optional[str]
    phonemizer: Optional[str]
    renderer_settings: Optional[URendererSettings]
    mute: Optional[bool]
    solo: Optional[bool]
    volume: Optional[int]


class UPitch(BaseModel):
    data: List[PitchData] = Field(
        default_factory=list
    )
    snap_first: Optional[bool]


class UVibrato(BaseModel):
    length: Optional[int]
    period: Optional[int]
    depth: Optional[int]
    in_value: Optional[int] = Field(
        alias="in"
    )
    out: Optional[int]
    shift: Optional[int]
    drift: Optional[int]


class UExpression(BaseModel):
    index: Optional[int]
    abbr: str
    value: int


class UPhonemeOverride(BaseModel):
    index: int
    phoneme: Optional[str]
    offset: Optional[int]
    preutter_delta: Optional[float]
    overlap_delta: Optional[float]


class UNote(BaseModel):
    position: Optional[int]
    duration: Optional[int]
    tone: Optional[int]
    lyric: Optional[str]
    pitch: Optional[UPitch]
    vibrato: Optional[UVibrato]
    note_expressions: Optional[List[UExpression]]  # deprecated
    phoneme_expressions: Optional[List[UExpression]]
    phoneme_overrides: Optional[List[UPhonemeOverride]]


class UPart(BaseModel):
    name: Optional[str]
    comment: Optional[str]
    track_no: Optional[int]
    position: Optional[int]


class UVoicePart(UPart):
    notes: List[UNote] = Field(
        default_factory=list
    )
    curves: List[UCurve] = Field(
        default_factory=list
    )


class UWavePart(UPart):
    relative_path: str
    file_duration_ms: float
    skip_ms: float
    trim_ms: float


class USTXProject(BaseModel):
    name: Optional[str]
    comment: Optional[str]
    output_dir: Optional[str]
    cache_dir: Optional[str]
    ustx_version: Optional[float]
    bpm: Optional[int]
    beat_per_bar: Optional[int]
    beat_unit: Optional[int]
    resolution: Optional[int]
    time_signatures: List[UTimeSignature] = Field(
        default_factory=list
    )
    tempos: List[UTempo] = Field(
        default_factory=list
    )
    expressions: Dict[str, UExpressionDescriptor]
    tracks: List[UTrack] = Field(
        default_factory=list
    )
    voice_parts: List[UVoicePart] = Field(
        default_factory=list
    )
    wave_parts: List[UWavePart] = Field(
        default_factory=list
    )
