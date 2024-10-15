from __future__ import annotations

import bisect
import functools
import math
from types import SimpleNamespace
from typing import Annotated, Literal, Optional, Union

from pydantic import Field, field_validator

from libresvip.core.constants import DEFAULT_BPM, TICKS_IN_BEAT
from libresvip.model.base import BaseModel
from libresvip.utils.audio import audio_path_validator
from libresvip.utils.music_math import linear_interpolation

ParamType = SimpleNamespace(
    CURVE="Curve",
    NUMERICAL="Numerical",
    OPTIONS="Options",
)


class BaseExpression(BaseModel):
    name: str
    abbr: str
    min_: float = Field(alias="min")
    max_: float = Field(alias="max")
    default_value: float
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
    def is_empty(self) -> bool:
        return len(self.xs) == 0 or all(y == 0 for y in self.ys)

    def sample(self, x: int) -> int:
        idx = bisect.bisect_left(self.xs, x)
        if idx < len(self.xs) and self.xs[idx] == x:
            return self.ys[idx]
        elif 0 < idx < len(self.xs):
            return round(
                linear_interpolation(
                    x,
                    (self.xs[idx - 1], self.ys[idx - 1]),
                    (self.xs[idx], self.ys[idx]),
                )
            )
        return 0


class PitchPoint(BaseModel):
    x: float
    y: float
    shape: Optional[Literal["io", "l", "i", "o"]] = "io"


class UTempo(BaseModel):
    position: int = 0
    bpm: float = DEFAULT_BPM


class UTimeSignature(BaseModel):
    bar_position: int = 0
    beat_per_bar: int = 4
    beat_unit: int = 4


class URendererSettings(BaseModel):
    renderer: Optional[str] = None
    resampler: Optional[str] = None
    wavtool: Optional[str] = None


class UTrack(BaseModel):
    track_name: Optional[str] = None
    track_color: Optional[str] = None
    voice_color_names: Optional[list[str]] = None
    singer: Optional[str] = None
    phonemizer: Optional[str] = None
    renderer_settings: Optional[URendererSettings] = None
    mute: bool = False
    solo: bool = False
    volume: float = 0.0
    pan: Optional[float] = None


class UPitch(BaseModel):
    data: list[PitchPoint] = Field(default_factory=list)
    snap_first: Optional[bool] = None


class UVibrato(BaseModel):
    length: float = 75.0
    period: float = 175.0
    depth: float = 25.0
    in_value: float = Field(10.0, alias="in")
    out: float = 10.0
    shift: float = 0.0
    drift: float = 0.0
    vol_link: float = 0.0

    @functools.cached_property
    def normalized_start(self) -> float:
        return 1.0 - self.length / 100.0

    def evaluate(self, n_pos: float, n_period: float, note: UNote) -> tuple[float, float]:
        n_start = self.normalized_start
        n_in = self.length / 100.0 * self.in_value / 100.0
        n_in_pos = n_start + n_in
        n_out = self.length / 100.0 * self.out / 100.0
        n_out_pos = 1.0 - n_out
        t = (n_pos - n_start) / n_period + self.shift / 100.0
        y = math.sin(math.tau * t) * self.depth
        if n_pos < n_start:
            y = 0.0
        elif n_pos < n_in_pos:
            y *= (n_pos - n_start) / n_in
        elif n_pos > n_out_pos:
            y *= (1.0 - n_pos) / n_out
        return (note.position + note.duration * n_pos, note.tone + y / 100.0)


class UExpression(BaseModel):
    index: Optional[int] = None
    abbr: str
    value: float


class UPhonemeOverride(BaseModel):
    index: int
    phoneme: Optional[str] = None
    offset: Optional[int] = None
    preutter_delta: Optional[float] = None
    overlap_delta: Optional[float] = None


class UNote(BaseModel):
    position: int
    duration: int
    tone: int
    lyric: str
    pitch: UPitch = Field(default_factory=UPitch)
    vibrato: UVibrato = Field(default_factory=UVibrato)
    note_expressions: Optional[list[UExpression]] = Field(default_factory=list)  # deprecated
    phoneme_expressions: Optional[list[UExpression]] = Field(default_factory=list)
    phoneme_overrides: Optional[list[UPhonemeOverride]] = Field(default_factory=list)

    @functools.cached_property
    def end(self) -> int:
        return self.position + self.duration


class UPart(BaseModel):
    name: str
    position: int = 0
    track_no: int
    comment: Optional[str] = None


class UVoicePart(UPart):
    notes: list[UNote] = Field(default_factory=list)
    curves: list[UCurve] = Field(default_factory=list)


class UWavePart(UPart):
    relative_path: str
    file_duration_ms: float = 0
    skip_ms: float = 0
    trim_ms: float = 0

    validate_relative_path = field_validator("relative_path", mode="before")(audio_path_validator)


class USTXProject(BaseModel):
    name: str = "New Project"
    comment: str = ""
    output_dir: str = "Vocal"
    cache_dir: str = "UCache"
    ustx_version: Union[str, float] = "0.6"
    bpm: float = DEFAULT_BPM
    beat_per_bar: int = 4
    beat_unit: int = 4
    resolution: int = TICKS_IN_BEAT
    time_signatures: list[UTimeSignature] = Field(default_factory=list)
    tempos: list[UTempo] = Field(default_factory=list)
    expressions: Optional[dict[str, UExpressionDescriptor]] = None
    tracks: list[UTrack] = Field(default_factory=list)
    voice_parts: list[UVoicePart] = Field(default_factory=list)
    wave_parts: list[UWavePart] = Field(default_factory=list)
    exp_selectors: Optional[list[str]] = None
    exp_primary: Optional[int] = 0
    exp_secondary: Optional[int] = 1
    key: Optional[int] = 0
