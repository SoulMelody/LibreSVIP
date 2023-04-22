import abc
from typing import Annotated, Literal, Union

from pydantic import Field

from libresvip.model.base import BaseModel


class DsMetadata(BaseModel):
    version: str = Field(alias="Version")
    name: str = Field(alias="Name")
    author: str = Field(alias="Author")


class DsControl(BaseModel):
    gain: float = 1.0
    mute: bool = False


class DsLoop(BaseModel):
    start: int = 0
    length: int = 0
    enabled: bool = True


class DsMaster(BaseModel):
    control: DsControl = Field(default_factory=DsControl)
    loop: DsLoop = Field(default_factory=DsLoop)


class DsLabel(BaseModel):
    pos: int = 0
    text: str = ""


class DsTempo(BaseModel):
    pos: int = 0
    value: float = 0.0


class DsTimeSignature(BaseModel):
    pos: int = 0
    numerator: int = 0
    denominator: int = 0


class DsTimeline(BaseModel):
    time_signatures: list[DsTimeSignature] = Field(
        default_factory=list, alias="timeSignatures"
    )
    tempos: list[DsTempo] = Field(default_factory=list)
    labels: list[DsLabel] = Field(default_factory=list)


class DsTime(BaseModel):
    start: int = 0
    length: int = 0
    clip_start: int = Field(0, alias="clipStart")
    clip_len: int = Field(0, alias="clipLen")


class DsParamNode(BaseModel):
    x: int = 0
    y: int = 0
    interp: Literal["linear", "hermite"] = "linear"


class DsParamFree(BaseModel):
    type_: Literal["free"] = Field("free", alias="type")
    start: int = 0
    step: int = 0
    values: list[int] = Field(default_factory=list)


class DsParamAnchor(BaseModel):
    type_: Literal["anchor"] = Field("anchor", alias="type")
    nodes: list[DsParamNode] = Field(default_factory=list)


DsParamCurve = Annotated[
    Union[DsParamFree, DsParamAnchor], Field(discriminator="type_")
]


class DsParam(BaseModel):
    original: DsParamCurve = Field(default_factory=DsParamFree)
    edited: DsParamCurve = Field(default_factory=DsParamFree)
    envelope: DsParamCurve = Field(default_factory=DsParamFree)


class DsParams(BaseModel):
    pitch: DsParam = Field(default_factory=DsParam)
    energy: DsParam = Field(default_factory=DsParam)


class DsVibratoPoint(BaseModel):
    x: int = 0
    y: int = 0


class DsVibrato(BaseModel):
    start: int = 0
    end: int = 0
    freq: float = 0.0
    phase: float = 0.0
    amp: float = 0.0
    offset: float = 0.0
    points: list[DsVibratoPoint] = Field(default_factory=list)


class DsPhoneme(BaseModel):
    type_: Literal["ahead", "normal", "final"] = Field("normal", alias="type")
    token: str = ""
    duration: int = 0
    extra: dict = Field(default_factory=dict)
    workspace: dict = Field(default_factory=dict)


class DsPhonemes(BaseModel):
    original: list[DsPhoneme] = Field(default_factory=list)
    edited: list[DsPhoneme] = Field(default_factory=list)


class DsNote(BaseModel):
    pos: int = 0
    length: int = 0
    key_num: int = Field(0, alias="keyNum")
    lyric: str = ""
    phonemes: DsPhonemes = Field(default_factory=DsPhonemes)
    vibrato: DsVibrato = Field(default_factory=DsVibrato)
    extra: dict = Field(default_factory=dict)
    workspace: dict = Field(default_factory=dict)


class DsClipMixin(abc.ABC):
    time: DsTime = Field(default_factory=DsTime)
    name: str = ""
    control: DsControl = Field(default_factory=DsControl)
    extra: dict = Field(default_factory=dict)
    workspace: dict = Field(default_factory=dict)


class DsAudioClip(DsClipMixin, BaseModel):
    type_: Literal["audio"] = Field("audio", alias="type")
    path: str = ""


class DsSingingClip(DsClipMixin, BaseModel):
    type_: Literal["singing"] = Field("singing", alias="type")
    sources: dict = Field(default_factory=dict)
    notes: list[DsNote] = Field(default_factory=list)


DsClip = Annotated[Union[DsAudioClip, DsSingingClip], Field(discriminator="type_")]


class DsTrackControl(BaseModel):
    gain: float = 1.0
    mute: bool = False
    solo: bool = False
    pan: float = 0.0


class DsTrack(BaseModel):
    name: str = ""
    control: DsTrackControl = Field(default_factory=DsTrackControl)
    clips: list[DsClip] = Field(default_factory=list)
    extra: dict = Field(default_factory=dict)
    workspace: dict = Field(default_factory=dict)


class DsContent(BaseModel):
    master: DsMaster = Field(default_factory=DsMaster)
    timeline: DsTimeline = Field(default_factory=DsTimeline)
    extra: dict = Field(default_factory=dict)
    workspace: dict = Field(default_factory=dict)
    params: DsParams = Field(default_factory=DsParams)
    tracks: list[DsTrack] = Field(default_factory=list)


class DspxModel(BaseModel):
    metadata: DsMetadata = Field(default_factory=DsMetadata)
    content: DsContent = Field(default_factory=DsContent)
    workspace: dict = Field(default_factory=dict)
