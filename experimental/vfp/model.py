from typing import Any, Optional

from pydantic import BaseModel, Field


class VOXFactoryNote(BaseModel):
    time: float
    midi: int
    name: str
    syllable: str
    ticks: int
    duration: float
    duration_ticks: int = Field(alias="durationTicks")
    velocity: int
    note_type: None = Field(alias="noteType")
    vibrato_depth: float = Field(alias="vibratoDepth")
    pre_bend: float = Field(alias="preBend")
    post_bend: float = Field(alias="postBend")
    harmonic_ratio: float = Field(alias="harmonicRatio")
    pitch_bends: list[float] = Field(alias="pitchBends")


class VOXFactoryMetadata(BaseModel):
    style: str
    accent: str
    transpose: int
    harmonic_ratio: float = Field(alias="harmonicRatio")
    pitch_detection: Optional[str] = Field(None, alias="pitchDetection")


class VOXFactoryClip(BaseModel):
    type: str
    length_type: str = Field(alias="lengthType")
    name: str
    start_quarter: int = Field(alias="startQuarter")
    offset_quarter: int = Field(alias="offsetQuarter")
    length: int
    note_bank: dict[str, VOXFactoryNote] = Field(alias="noteBank")
    note_order: list[str] = Field(alias="noteOrder")
    next_note_index: int = Field(alias="nextNoteIndex")
    use_source: bool = Field(alias="useSource")
    pinned_audio_data_order: list[str] = Field(alias="pinnedAudioDataOrder")
    audio_data_order: list[str] = Field(alias="audioDataOrder")
    audio_data_quarter: int = Field(alias="audioDataQuarter")
    metadata: VOXFactoryMetadata
    audio_data_key: str = Field(alias="audioDataKey")


class VOXFactoryAudioViewProperty(BaseModel):
    view: str
    colormap: str
    window: str
    window_size: int = Field(alias="windowSize")
    hop_size: int = Field(alias="hopSize")
    f_min: float = Field(alias="fMin")
    f_max: None = Field(alias="fMax")
    level_min: None = Field(alias="levelMin")
    level_max: None = Field(alias="levelMax")
    level_scale: str = Field(alias="levelScale")
    num_bins: int = Field(alias="numBins")
    bins_per_octave: int = Field(alias="binsPerOctave")


class VOXFactoryDevice(BaseModel):
    type: str
    track_type: str = Field(alias="trackType")
    name: str
    data: dict[str, Any]
    on: bool


class VOXFactoryTrack(BaseModel):
    type: str
    name: str
    instrument: str
    h: int
    color: str
    volume: float
    pan: float
    solo: bool
    mute: bool
    arm: bool
    clip_bank: dict[str, VOXFactoryClip] = Field(alias="clipBank")
    clip_order: list[str] = Field(alias="clipOrder")
    device_bank: dict[str, VOXFactoryDevice] = Field(alias="deviceBank")
    device_order: list[str] = Field(alias="deviceOrder")
    audio_view_property: VOXFactoryAudioViewProperty = Field(alias="audioViewProperty")


class VOXFactorySelectedClipBankItem(BaseModel):
    track_key: str = Field(alias="trackKey")
    clip_key: str = Field(alias="clipKey")


class VOXFactorySelectedNoteBankItem(BaseModel):
    track_key: str = Field(alias="trackKey")
    clip_key: str = Field(alias="clipKey")
    note_key: str = Field(alias="noteKey")


class VOXFactoryAudioData(BaseModel):
    sample_rate: int = Field(alias="sampleRate")
    number_of_channels: int = Field(alias="numberOfChannels")
    sample_length: int = Field(alias="sampleLength")
    metadata: VOXFactoryMetadata


class VOXFactoryProject(BaseModel):
    version: str
    tempo: float
    time_signature: list[int] = Field(alias="timeSignature")
    project_name: str = Field(alias="projectName")
    track_bank: dict[str, VOXFactoryTrack] = Field(alias="trackBank")
    track_order: list[str] = Field(alias="trackOrder")
    selected_track_bank: list[str] = Field(alias="selectedTrackBank")
    selected_clip_bank: list[VOXFactorySelectedClipBankItem] = Field(alias="selectedClipBank")
    selected_note_bank: list[VOXFactorySelectedNoteBankItem] = Field(alias="selectedNoteBank")
    audio_data_bank: dict[str, VOXFactoryAudioData] = Field(alias="audioDataBank")
