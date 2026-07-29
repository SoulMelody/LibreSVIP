from __future__ import annotations

import math
from typing import Annotated, Any, Literal

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    RootModel,
    model_validator,
)

INT32_MIN = -(2**31)
INT32_MAX = 2**31 - 1


def _validate_json_int(value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        msg = "Input should be a JSON integer"
        raise ValueError(msg)
    return value


def _validate_json_number(value: Any) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        msg = "Input should be a JSON number"
        raise ValueError(msg)
    result = float(value)
    if not math.isfinite(result):
        msg = "Input should be a finite JSON number"
        raise ValueError(msg)
    return result


JsonInt = Annotated[int, BeforeValidator(_validate_json_int)]
JsonNumber = Annotated[float, BeforeValidator(_validate_json_number)]
Int32 = Annotated[JsonInt, Field(ge=INT32_MIN, le=INT32_MAX)]
NonNegativeInt32 = Annotated[JsonInt, Field(ge=0, le=INT32_MAX)]
UnitNumber = Annotated[JsonNumber, Field(ge=0, le=1)]
CentShift = Annotated[JsonInt, Field(ge=-50, le=50)]
MidiKey = Annotated[JsonInt, Field(ge=0, le=127)]
TempoValue = Annotated[JsonNumber, Field(ge=10, le=1000)]
Pan = Annotated[JsonNumber, Field(ge=-1, le=1)]
Workspace = dict[str, dict[str, Any]]


class DspxBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class DspxRootModel(RootModel[Any]):
    model_config = ConfigDict(strict=True)


class BusControl(DspxBaseModel):
    gain: JsonNumber
    mute: bool
    pan: Pan


class TrackControl(BusControl):
    solo: bool


class ClipTime(DspxBaseModel):
    clipLen: NonNegativeInt32
    clipStart: NonNegativeInt32
    length: NonNegativeInt32
    pos: NonNegativeInt32


class ControlPoint(DspxBaseModel):
    x: JsonNumber
    y: JsonNumber


class VibratoPoints(DspxBaseModel):
    amp: list[ControlPoint]
    freq: list[ControlPoint]


class Vibrato(DspxBaseModel):
    start: UnitNumber
    end: UnitNumber
    amp: Annotated[JsonInt, Field(ge=0, le=INT32_MAX)]
    freq: Annotated[JsonNumber, Field(ge=0)]
    phase: UnitNumber
    offset: Int32
    points: VibratoPoints


class Pronunciation(DspxBaseModel):
    original: str
    edited: str


class Phoneme(DspxBaseModel):
    language: str
    start: Int32
    token: str
    onset: bool


class Phonemes(DspxBaseModel):
    original: list[Phoneme]
    edited: list[Phoneme]


class Note(DspxBaseModel):
    pos: NonNegativeInt32
    length: NonNegativeInt32
    keyNum: MidiKey
    centShift: CentShift
    language: str
    lyric: str
    pronunciation: Pronunciation
    phonemes: Phonemes
    vibrato: Vibrato
    workspace: Workspace


class ParamCurveFree(DspxBaseModel):
    type: Literal["free"]
    start: Int32
    step: Literal[5]
    values: list[Int32]


class AnchorNode(DspxBaseModel):
    interp: Literal["none", "linear", "hermite"]
    x: NonNegativeInt32
    y: Int32


class ParamCurveAnchor(DspxBaseModel):
    type: Literal["anchor"]
    start: Int32
    nodes: list[AnchorNode]


ParamCurve = Annotated[ParamCurveAnchor | ParamCurveFree, Field(discriminator="type")]


class Param(DspxBaseModel):
    edited: list[ParamCurve]
    transform: list[ParamCurve]
    original: list[ParamCurve]


class SingleSinger(DspxBaseModel):
    type: Literal["single"]
    id: str
    extra: Any
    workspace: Workspace


class MixedSinger(DspxBaseModel):
    type: Literal["mixed"]
    singers: list[Singer]
    ratio: list[UnitNumber]
    extra: Any
    workspace: Workspace

    @model_validator(mode="after")
    def validate_ratio(self) -> MixedSinger:
        if not self.singers:
            msg = "Mixed singer must contain at least one singer"
            raise ValueError(msg)
        if len(self.ratio) + 1 != len(self.singers) or sum(self.ratio) > 1:
            msg = "Invalid singer mixing ratio"
            raise ValueError(msg)
        return self


Singer = Annotated[SingleSinger | MixedSinger, Field(discriminator="type")]


class DynamicMixingAnchor(DspxBaseModel):
    pos: NonNegativeInt32
    ratio: list[UnitNumber]


class Sources(DspxBaseModel):
    category: str
    mix: list[DynamicMixingAnchor]
    singers: Annotated[list[Singer], Field(min_length=1)]

    @model_validator(mode="after")
    def validate_ratios(self) -> Sources:
        for anchor in self.mix:
            if len(anchor.ratio) + 1 != len(self.singers) or sum(anchor.ratio) > 1:
                msg = "Invalid dynamic mixing ratio"
                raise ValueError(msg)
        return self


class AudioClip(DspxBaseModel):
    type: Literal["audio"]
    name: str
    path: str
    time: ClipTime
    control: BusControl
    workspace: Workspace


class SingingClip(DspxBaseModel):
    type: Literal["singing"]
    name: str
    time: ClipTime
    control: BusControl
    notes: list[Note]
    params: dict[str, Param]
    sources: Sources | None
    workspace: Workspace


Clip = Annotated[AudioClip | SingingClip, Field(discriminator="type")]


class Track(DspxBaseModel):
    name: str
    control: TrackControl
    clips: list[Clip]
    workspace: Workspace


class Tempo(DspxBaseModel):
    pos: NonNegativeInt32
    value: TempoValue


class TimeSignature(DspxBaseModel):
    index: NonNegativeInt32
    numerator: Annotated[JsonInt, Field(ge=1, le=INT32_MAX)]
    denominator: Literal[1, 2, 4, 8, 16, 32, 64, 128]


class Label(DspxBaseModel):
    pos: NonNegativeInt32
    text: str


class Timeline(DspxBaseModel):
    labels: list[Label]
    tempos: list[Tempo]
    timeSignatures: list[TimeSignature]


class Global(DspxBaseModel):
    author: str
    centShift: CentShift
    editorId: str
    editorName: str
    name: str


class Master(DspxBaseModel):
    control: BusControl


class Content(DspxBaseModel):
    global_: Global = Field(alias="global")
    master: Master
    timeline: Timeline
    tracks: list[Track]
    workspace: Workspace

    model_config = ConfigDict(extra="forbid", strict=True, populate_by_name=True)


class Model(DspxBaseModel):
    content: Content
    version: Literal["1.0.0"]


MixedSinger.model_rebuild()
Sources.model_rebuild()
Track.model_rebuild()

