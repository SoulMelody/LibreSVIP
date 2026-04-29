from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import BaseModel, Field


class TimeSignature(BaseModel):
    numerator: int
    denominator: int


class BpmEvent(BaseModel):
    position: int
    bpm: float


class TimeSignatureEvent(BaseModel):
    position: int
    time_sig: TimeSignature


class Setup(BaseModel):
    ppq: float
    bpm: float
    time_signature: TimeSignature
    bpm_events: list[BpmEvent]
    time_signature_events: list[TimeSignatureEvent]


class Settings(BaseModel):
    legacy_input: bool


class MainOut(BaseModel):
    id: str
    name: str


class Mixer(BaseModel):
    gain: float
    pan: float
    record_arm: bool
    solo: bool
    mute: bool
    output: str
    bus: str
    sends: list[Any]


class MsqSinger(BaseModel):
    name: str
    id: str
    primary_expression: str
    loaded_expressions: list[str]
    language: str
    accent: str
    phoneset: str


class SingerInstrument(BaseModel):
    singer: MsqSinger = Field(..., alias="Singer")


class Color(BaseModel):
    track_color: str = Field(..., alias="TrackColor")


class Phoneme(BaseModel):
    phoneme: str
    time: int
    velocity: int
    lock_timing: bool


class MsqNote(BaseModel):
    id: str
    clip_id: str
    start: int
    length: int
    pitch: float
    lyric: str
    phonemes: list[Phoneme]


class Parameter(BaseModel):
    value: float


class Parameters(BaseModel):
    breathiness: Parameter = Field(..., alias="Breathiness")
    tension: Parameter = Field(..., alias="Tension")
    pitch_transition: Parameter = Field(..., alias="PitchTransition")
    vibrato_rate: Parameter = Field(..., alias="VibratoRate")
    character: Parameter = Field(..., alias="Character")
    vibrato_depth: Parameter = Field(..., alias="VibratoDepth")
    pitch: Parameter = Field(..., alias="Pitch")
    roughness: Parameter = Field(..., alias="Roughness")
    stability: Parameter = Field(..., alias="Stability")
    dynamics: Parameter = Field(..., alias="Dynamics")


class Audio(BaseModel):
    path: str
    start: float
    speed: float
    bpm: float


class MsqBaseClip(BaseModel):
    id: str
    track_id: str
    name: str
    color: str | Color
    start: int
    length: int


class MsqSingerClip(MsqBaseClip):
    kind: Literal["Singer"] = "Singer"
    notes: list[MsqNote] | None = None
    parameters: Parameters | None = None


class MsqAudioClip(MsqBaseClip):
    kind: Literal["Audio"] = "Audio"
    audio: Audio | None = None


class MsqBaseTrack(BaseModel):
    id: str
    mixer: Mixer
    name: str
    color: str
    index: int
    effects: Any | None = None
    tracks: list[Any]


class MsqSingerTrack(MsqBaseTrack):
    track_type: Literal["Singer"] = "Singer"
    instrument: SingerInstrument
    clips: list[MsqSingerClip]


class MsqAudioTrack(MsqBaseTrack):
    track_type: Literal["Audio"] = "Audio"
    instrument: str
    clips: list[MsqAudioClip]


MsqTrack = Annotated[
    MsqSingerTrack | MsqAudioTrack,
    Field(discriminator="track_type"),
]


class MikotoStudioSequenceFormat(BaseModel):
    id: str
    version: int
    setup: Setup
    settings: Settings
    main_out: MainOut
    aux: list[Any]
    tracks: list[MsqTrack]
