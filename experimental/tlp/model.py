from __future__ import annotations

from typing import Annotated, Any, Literal, Optional, Union

from pydantic import Field

from libresvip.model.base import BaseModel


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
    values: list[float] = Field(default_factory=list)


class TuneLabAutomations(BaseModel):
    brightness: Optional[TuneLabAutomation] = Field(None, alias="Brightness")
    clearness: Optional[TuneLabAutomation] = Field(None, alias="Clearness")
    dynamics: Optional[TuneLabAutomation] = Field(None, alias="Dynamics")
    gender: Optional[TuneLabAutomation] = Field(None, alias="Gender")
    growl: Optional[TuneLabAutomation] = Field(None, alias="Growl")
    pitch_bend: Optional[TuneLabAutomation] = Field(None, alias="PitchBend")
    pitch_bend_sensitivity: Optional[TuneLabAutomation] = Field(None, alias="PitchBendSensitivity")
    vibrato_envelope: Optional[TuneLabAutomation] = Field(None, alias="VibratoEnvelope")
    volume: Optional[TuneLabAutomation] = Field(None, alias="Volume")


class TuneLabAffectedAutomations(BaseModel):
    brightness: Optional[float] = Field(None, alias="Brightness")
    clearness: Optional[float] = Field(None, alias="Clearness")
    dynamics: Optional[float] = Field(None, alias="Dynamics")
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


class BasePart(BaseModel):
    name: str
    pos: float
    dur: float


class TuneLabMidiPart(BasePart):
    type_: Literal["midi"] = Field(alias="type")
    gain: Optional[float] = 0.0
    voice: TuneLabVoice
    properties: dict[str, Any] = Field(default_factory=dict)
    notes: list[TuneLabNote] = Field(default_factory=list)
    automations: Optional[TuneLabAutomations] = None
    pitch: list[list[float]]
    vibratos: list[TuneLabVibrato] = Field(default_factory=list)


class TuneLabAudioPart(BasePart):
    type_: Literal["audio"] = Field(alias="type")
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
