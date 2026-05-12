from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import Field

from libresvip.model.base import BaseModel
from libresvip.utils.text import uuid_str


class MsqTimeSignature(BaseModel):
    numerator: int
    denominator: int


class MsqBpmEvent(BaseModel):
    position: int
    bpm: float


class MsqTimeSignatureEvent(BaseModel):
    position: int
    time_sig: MsqTimeSignature


class MsqSetup(BaseModel):
    ppq: float
    bpm: float
    time_signature: MsqTimeSignature
    bpm_events: list[MsqBpmEvent]
    time_signature_events: list[MsqTimeSignatureEvent]


class MsqSettings(BaseModel):
    legacy_input: bool = False


class MsqMainOut(BaseModel):
    id: str = Field(default_factory=uuid_str)
    name: str = "Main Out"


class MsqMixer(BaseModel):
    gain: float
    pan: float
    record_arm: bool
    solo: bool
    mute: bool
    output: str
    bus: str = Field(default_factory=uuid_str)
    sends: list[Any] = Field(default_factory=list)


class MsqSinger(BaseModel):
    name: str
    id: str
    primary_expression: str = Field(default_factory=uuid_str)
    loaded_expressions: list[str] = Field(default_factory=list)
    language: str = "SingerDefault"
    accent: str = "SingerDefault"
    phoneset: str = "SingerDefault"


class MsqSingerInstrument(BaseModel):
    singer: MsqSinger = Field(..., alias="Singer")


class MsqColor(BaseModel):
    track_color: str = Field(..., alias="TrackColor")


class MsqPhoneme(BaseModel):
    phoneme: str
    time: int
    velocity: int
    lock_timing: bool


class MsqNote(BaseModel):
    id: str = Field(default_factory=uuid_str)
    clip_id: str
    start: int
    length: int
    pitch: float
    lyric: str
    phonemes: list[MsqPhoneme]


class MsqPoint(BaseModel):
    time: int
    value: float


class MsqParameter(BaseModel):
    value: float = 0.0
    points: list[MsqPoint] = Field(default_factory=list)


class MsqParameters(BaseModel):
    breathiness: MsqParameter = Field(default_factory=MsqParameter, alias="Breathiness")
    tension: MsqParameter = Field(default_factory=MsqParameter, alias="Tension")
    pitch_transition: MsqParameter = Field(default_factory=MsqParameter, alias="PitchTransition")
    vibrato_rate: MsqParameter = Field(default_factory=MsqParameter, alias="VibratoRate")
    character: MsqParameter = Field(default_factory=MsqParameter, alias="Character")
    vibrato_depth: MsqParameter = Field(default_factory=MsqParameter, alias="VibratoDepth")
    pitch: MsqParameter = Field(default_factory=MsqParameter, alias="Pitch")
    roughness: MsqParameter = Field(default_factory=MsqParameter, alias="Roughness")
    stability: MsqParameter = Field(default_factory=MsqParameter, alias="Stability")
    dynamics: MsqParameter = Field(default_factory=MsqParameter, alias="Dynamics")


class MsqAudio(BaseModel):
    path: str
    start: float
    speed: float
    bpm: float


class MsqBaseClip(BaseModel):
    id: str = Field(default_factory=uuid_str)
    clip_id: str | None = None
    track_id: str
    name: str
    color: str | MsqColor
    start: int
    length: int


class MsqSingerClip(MsqBaseClip):
    kind: Literal["Singer"] = "Singer"
    notes: list[MsqNote] | None = None
    parameters: MsqParameters | None = None


class MsqAudioClip(MsqBaseClip):
    kind: Literal["Audio"] = "Audio"
    audio: MsqAudio | None = None


class MsqBaseTrack(BaseModel):
    id: str = Field(default_factory=uuid_str)
    mixer: MsqMixer
    name: str
    color: str
    index: int
    effects: Any | None = None
    tracks: list[Any] = Field(default_factory=list)


class MsqSingerTrack(MsqBaseTrack):
    track_type: Literal["Singer"] = "Singer"
    instrument: MsqSingerInstrument
    clips: list[MsqSingerClip]


class MsqAudioTrack(MsqBaseTrack):
    track_type: Literal["Audio"] = "Audio"
    instrument: str = "AudioPlayer"
    clips: list[MsqAudioClip]


MsqTrack = Annotated[
    MsqSingerTrack | MsqAudioTrack,
    Field(discriminator="track_type"),
]


class MikotoStudioSequenceFormat(BaseModel):
    id: str = Field(default_factory=uuid_str)
    setup: MsqSetup
    main_out: MsqMainOut
    aux: list[Any] = Field(default_factory=list)
    tracks: list[MsqTrack] = Field(default_factory=list)
    settings: MsqSettings = Field(default_factory=MsqSettings)
    version: int = 110
