from __future__ import annotations

from typing import Any

from libresvip.model.base import BaseModel


class TempoEvent(BaseModel):
    beat: float
    bpm: float


class TimeSigEvent(BaseModel):
    measure: int
    numerator: int
    denominator: int


class Primary(BaseModel):
    name: str
    intensity: int


class Secondary(BaseModel):
    name: Any | None
    intensity: int


class StyleMix(BaseModel):
    primary: Primary
    secondary: Secondary


class Vibrato(BaseModel):
    enabled: bool
    rate_hz: float
    depth_cent: float
    start_ratio: float
    fade_in_ms: float
    mix_ratio: float


class Dynamics(BaseModel):
    gain_db: float


class Note(BaseModel):
    id: str
    lyric: str
    phonemes: list[str]
    phoneme_starts_ms: list[float]
    notenum: int
    start_ms: float
    duration_ms: float
    consonant_velocity: float
    style_mix: StyleMix
    vibrato: Vibrato | None
    dynamics: Dynamics | None
    voice_mix: dict[str, list[int]]
    clip_id: str
    gacha_seed: int


class PitchControlPoint(BaseModel):
    time_ms: float
    cent: float
    note_id: str


class Clip(BaseModel):
    id: str
    start_ms: float
    end_ms: float
    name: Any | None
    color: Any | None
    fade_in_ms: float
    fade_out_ms: float
    fade_tension: float
    fade_scurve: bool
    audio_src_offset_ms: Any | None
    pitch_correction: Any | None


class Track(BaseModel):
    id: str
    name: str
    kind: str
    ust_path: Any | None
    model_path: str | None
    notes: list[Note]
    pitch_control_points: list[PitchControlPoint]
    timing_overrides: list[Any]
    dynamics_envelope: list[Any]
    original_f0_cache: Any | None
    audio_src: str | None
    audio_offset_ms: float
    mute: bool
    solo: bool
    volume: float
    pan: float
    fx: Any | None
    color: str
    height: float
    clips: list[Clip]


class NepFormat(BaseModel):
    format: str
    version: int


class NepProject(BaseModel):
    version: str
    ust_path: Any | None
    model_path: Any | None
    tempo: float
    tempo_events: list[TempoEvent]
    time_sig_events: list[TimeSigEvent]
    tracks: list[Track]
    active_track_id: str
