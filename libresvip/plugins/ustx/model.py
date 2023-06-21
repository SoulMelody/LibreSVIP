import math
from types import SimpleNamespace
from typing import Annotated, Literal, Optional, Union

from pydantic import Field

from libresvip.model.base import BaseModel

from libresvip.core.constants import TICKS_IN_BEAT
from libresvip.model.base import Point

from .utils.music_math import MusicMath

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
    options: list[str] = Field(default_factory=list)


UExpressionDescriptor = Annotated[
    Union[CurveExpression, NumericalExpression, OptionsExpression],
    Field(discriminator="type_"),
]


class UCurve(BaseModel):
    xs: list[int] = Field(default_factory=list)
    ys: list[int] = Field(default_factory=list)
    abbr: Optional[str] = None

    @property
    def is_empty(self):
        return len(self.xs) == 0 or all(y == 0 for y in self.ys)

    def sample(self, x):
        if x in self.xs:
            idx = self.xs.index(x)
            return self.ys[idx]
        else:
            idx = -1
        idx = ~idx
        if 0 < idx < len(self.xs):
            return round(MusicMath.linear(self.xs[idx - 1], self.xs[idx], self.ys[idx - 1], self.ys[idx], x))
        return 0


class PitchPoint(BaseModel):
    x: Optional[int] = None
    y: Optional[int] = None
    shape: Optional[Literal["io", "l", "i", "o"]] = "io"


class UTempo(BaseModel):
    position: Optional[int] = None
    bpm: Optional[int] = None


class UTimeSignature(BaseModel):
    bar_position: Optional[int] = None
    beat_per_bar: Optional[int] = None
    beat_unit: Optional[int] = None


class URendererSettings(BaseModel):
    renderer: Optional[str] = None
    resampler: Optional[str] = None
    wavtool: Optional[str] = None


class UTrack(BaseModel):
    singer: Optional[str] = None
    phonemizer: Optional[str] = None
    renderer_settings: Optional[URendererSettings] = None
    mute: Optional[bool] = None
    solo: Optional[bool] = None
    volume: Optional[int] = None


class UPitch(BaseModel):
    data: list[PitchPoint] = Field(default_factory=list)
    snap_first: Optional[bool] = None


class UVibrato(BaseModel):
    length: Optional[int] = None
    period: Optional[int] = None
    depth: Optional[int] = None
    in_value: Optional[int] = Field(alias="in")
    out: Optional[int] = None
    shift: Optional[int] = None
    drift: Optional[int] = None

    @property
    def normalized_start(self):
        return 1.0 - self.length / 100.0

    def evaluate(self, n_pos, n_period, note: 'UNote') -> Point:
        n_start = self.normalized_start
        n_in = self.length / 100.0 * self.in_value / 100.0
        n_in_pos = n_start + n_in
        n_out = self.length / 100.0 * self.out / 100.0
        n_out_pos = 1.0 - n_out
        t = (n_pos - n_start) / n_period + self.shift / 100.0
        y = math.sin(2 * math.pi * t) * self.depth
        if n_pos < n_start:
            y = 0.0
        elif n_pos < n_in_pos:
            y *= (n_pos - n_start) / n_in
        elif n_pos > n_out_pos:
            y *= (1.0 - n_pos) / n_out
        return Point(note.position + note.duration * n_pos, note.tone + y / 100.0)


class UExpression(BaseModel):
    index: Optional[int] = None
    abbr: str
    value: int


class UPhonemeOverride(BaseModel):
    index: int
    phoneme: Optional[str] = None
    offset: Optional[int] = None
    preutter_delta: Optional[float] = None
    overlap_delta: Optional[float] = None


class UNote(BaseModel):
    position: Optional[int] = None
    duration: Optional[int] = None
    tone: Optional[int] = None
    lyric: Optional[str] = None
    pitch: Optional[UPitch] = None
    vibrato: Optional[UVibrato] = None
    note_expressions: Optional[list[UExpression]] = Field(default_factory=list)  # deprecated
    phoneme_expressions: Optional[list[UExpression]] = Field(default_factory=list)
    phoneme_overrides: Optional[list[UPhonemeOverride]] = Field(default_factory=list)

    @property
    def end(self) -> int:
        return self.position + self.duration


class UPart(BaseModel):
    name: Optional[str] = None
    comment: Optional[str] = None
    track_no: Optional[int] = None
    position: Optional[int] = None


class UVoicePart(UPart):
    notes: list[UNote] = Field(
        default_factory=list
    )
    curves: list[UCurve] = Field(
        default_factory=list
    )


class UWavePart(UPart):
    relative_path: str
    file_duration_ms: float = 0
    skip_ms: float = 0
    trim_ms: float = 0


class USTXProject(BaseModel):
    name: Optional[str] = None
    comment: Optional[str] = None
    output_dir: Optional[str] = None
    cache_dir: Optional[str] = None
    ustx_version: Optional[float] = None
    bpm: Optional[int] = None
    beat_per_bar: Optional[int] = None
    beat_unit: Optional[int] = None
    resolution: Optional[int] = TICKS_IN_BEAT
    time_signatures: list[UTimeSignature] = Field(
        default_factory=list
    )
    tempos: list[UTempo] = Field(
        default_factory=list
    )
    expressions: dict[str, UExpressionDescriptor] = Field(
        default_factory=dict
    )
    tracks: list[UTrack] = Field(
        default_factory=list
    )
    voice_parts: list[UVoicePart] = Field(
        default_factory=list
    )
    wave_parts: list[UWavePart] = Field(
        default_factory=list
    )
