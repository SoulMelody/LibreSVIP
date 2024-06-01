from __future__ import annotations

from itertools import chain
from typing import Annotated, Any, Literal, NamedTuple, Optional, Union

from more_itertools import batched
from pydantic import Field, RootModel, ValidationInfo, field_validator, model_serializer

from libresvip.model.base import BaseModel
from libresvip.model.point import PointList


class TuneLabPoint(NamedTuple):
    pos: float
    value: float


class TuneLabPoints(PointList[TuneLabPoint], RootModel[list[TuneLabPoint]]):
    root: list[TuneLabPoint] = Field(default_factory=list)

    @model_serializer(when_used="json")
    def serialize_points(self) -> list[float]:
        return list(chain.from_iterable(self.root))


class TuneLabTempo(BaseModel):
    pos: float
    bpm: float


class TuneLabTimeSignature(BaseModel):
    numerator: int
    denominator: int
    bar_index: int = Field(alias="barIndex")


class TuneLabVoice(BaseModel):
    type_: str = Field("", alias="type")
    id_: str = Field("", alias="id")


class TuneLabAutomation(BaseModel):
    default: float
    values: TuneLabPoints = Field(default_factory=TuneLabPoints)

    @field_validator("values", mode="before")
    @classmethod
    def validate_values(
        cls, values: list[Union[float, TuneLabPoint]], _info: ValidationInfo
    ) -> TuneLabPoints:
        if _info.mode == "json":
            return TuneLabPoints(root=[TuneLabPoint._make(each) for each in batched(values, 2)])
        return TuneLabPoints(root=values)


class TuneLabAutomations(BaseModel):
    air: Optional[TuneLabAutomation] = Field(None, alias="Air")
    breathiness: Optional[TuneLabAutomation] = Field(None, alias="Breathiness")
    brightness: Optional[TuneLabAutomation] = Field(None, alias="Brightness")
    clearness: Optional[TuneLabAutomation] = Field(None, alias="Clearness")
    dynamics: Optional[TuneLabAutomation] = Field(None, alias="Dynamics")
    exciter: Optional[TuneLabAutomation] = Field(None, alias="Exciter")
    gender: Optional[TuneLabAutomation] = Field(None, alias="Gender")
    growl: Optional[TuneLabAutomation] = Field(None, alias="Growl")
    pitch_bend: Optional[TuneLabAutomation] = Field(None, alias="PitchBend")
    pitch_bend_sensitivity: Optional[TuneLabAutomation] = Field(None, alias="PitchBendSensitivity")
    vibrato_envelope: Optional[TuneLabAutomation] = Field(None, alias="VibratoEnvelope")
    volume: Optional[TuneLabAutomation] = Field(None, alias="Volume")


class TuneLabAffectedAutomations(BaseModel):
    air: Optional[float] = Field(None, alias="Air")
    breathiness: Optional[float] = Field(None, alias="Breathiness")
    brightness: Optional[float] = Field(None, alias="Brightness")
    clearness: Optional[float] = Field(None, alias="Clearness")
    dynamics: Optional[float] = Field(None, alias="Dynamics")
    exciter: Optional[float] = Field(None, alias="Exciter")
    gender: Optional[float] = Field(None, alias="Gender")
    growl: Optional[float] = Field(None, alias="Growl")
    pitch_bend: Optional[float] = Field(None, alias="PitchBend")
    pitch_bend_sensitivity: Optional[float] = Field(None, alias="PitchBendSensitivity")
    vibrato_envelope: Optional[float] = Field(None, alias="VibratoEnvelope")
    volume: Optional[float] = Field(None, alias="Volume")


class TuneLabPhoneme(BaseModel):
    start_time: float = Field(alias="startTime")
    end_time: float = Field(alias="endTime")
    symbol: str


class TuneLabNote(BaseModel):
    pos: float
    dur: float
    pitch: int
    lyric: str
    pronunciation: Optional[str] = None
    phonemes: list[TuneLabPhoneme] = Field(default_factory=list)
    properties: dict[str, Any] = Field(default_factory=dict)


class TuneLabVibrato(BaseModel):
    pos: float
    dur: float
    frequency: float
    amplitude: float
    phase: float
    attack: float
    release: float
    affected_automations: Optional[TuneLabAffectedAutomations] = Field(
        None, alias="affectedAutomations"
    )


class TuneLabBasePart(BaseModel):
    name: str
    pos: float
    dur: float


class TuneLabMidiPart(TuneLabBasePart):
    type_: Literal["midi"] = Field("midi", alias="type")
    gain: Optional[float] = 0.0
    voice: TuneLabVoice = Field(default_factory=TuneLabVoice)
    properties: dict[str, Any] = Field(default_factory=dict)
    notes: list[TuneLabNote] = Field(default_factory=list)
    automations: Optional[TuneLabAutomations] = None
    pitch: list[TuneLabPoints] = Field(default_factory=list)
    vibratos: list[TuneLabVibrato] = Field(default_factory=list)

    @field_validator("pitch", mode="before")
    @classmethod
    def validate_pitch(
        cls, pitch: list[Union[list[float], TuneLabPoints]], _info: ValidationInfo
    ) -> TuneLabPoints:
        if _info.mode == "json":
            return [
                TuneLabPoints(root=[TuneLabPoint._make(each) for each in batched(values, 2)])
                for values in pitch
            ]
        return pitch


class TuneLabAudioPart(TuneLabBasePart):
    type_: Literal["audio"] = Field("audio", alias="type")
    path: str


TuneLabPart = Annotated[Union[TuneLabMidiPart, TuneLabAudioPart], Field(discriminator="type_")]


class TuneLabTrack(BaseModel):
    name: str
    gain: float
    pan: float
    mute: bool
    solo: bool
    parts: list[TuneLabPart] = Field(default_factory=list)


class TuneLabProject(BaseModel):
    version: int = 0
    tempos: list[TuneLabTempo] = Field(default_factory=list)
    time_signatures: list[TuneLabTimeSignature] = Field(
        default_factory=list, alias="timeSignatures"
    )
    tracks: list[TuneLabTrack] = Field(default_factory=list)
