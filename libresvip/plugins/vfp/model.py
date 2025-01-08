import pathlib
from typing import Annotated, Any, Literal, Optional, Union

from pydantic import Field, ValidationInfo, model_validator
from typing_extensions import Self

from libresvip.model.base import BaseModel


class VOXFactoryNote(BaseModel):
    time: float
    midi: int
    name: str
    syllable: str
    ticks: float
    duration_ticks: float = Field(alias="durationTicks")
    duration: float = 0.25
    velocity: int = 1
    note_type: Optional[str] = Field(None, alias="noteType")
    vibrato_depth: Optional[float] = Field(None, alias="vibratoDepth")
    pre_bend: Optional[float] = Field(None, alias="preBend")
    post_bend: Optional[float] = Field(None, alias="postBend")
    harmonic_ratio: Optional[float] = Field(None, alias="harmonicRatio")
    pitch_bends: list[float] = Field(default_factory=list, alias="pitchBends")


class VOXFactoryMetadata(BaseModel):
    style: str
    accent: str
    transpose: int
    harmonic_ratio: float = Field(alias="harmonicRatio")
    pitch_detection: Optional[str] = Field(None, alias="pitchDetection")
    instrument: Optional[str] = None


class VOXFactoryClipBase(BaseModel):
    name: str = ""
    start_quarter: float = Field(0, alias="startQuarter")
    offset_quarter: float = Field(0, alias="offsetQuarter")
    length: float
    use_source: bool = Field(True, alias="useSource")
    audio_data_key: Optional[str] = Field(None, alias="audioDataKey")
    audio_data_order: list[str] = Field(default_factory=list, alias="audioDataOrder")
    audio_data_quarter: float = Field(0, alias="audioDataQuarter")
    note_bank: dict[str, VOXFactoryNote] = Field(default_factory=dict, alias="noteBank")
    note_order: list[str] = Field(default_factory=list, alias="noteOrder")
    next_note_index: int = Field(0, alias="nextNoteIndex")
    pinned_audio_data_order: list[str] = Field(default_factory=list, alias="pinnedAudioDataOrder")
    metadata: Optional[VOXFactoryMetadata] = None


class VOXFactoryVocalClip(VOXFactoryClipBase):
    type: Literal["vocal"] = "vocal"
    length_type: Literal["quarter"] = Field("quarter", alias="lengthType")


class VOXFactoryAudioClip(VOXFactoryClipBase):
    type: Literal["audio"] = "audio"
    length_type: Literal["time"] = Field("time", alias="lengthType")
    source_audio_data_key: str = Field(alias="sourceAudioDataKey")

    @model_validator(mode="after")
    def extract_audio(self, info: ValidationInfo) -> Self:
        if (
            info.context is not None
            and info.context["extract_audio"]
            and not hasattr(info.context["path"], "protocol")
        ):
            archive_audio_path = f"resources/{self.source_audio_data_key}"
            if not (
                audio_path := (info.context["path"].parent / self.name).with_suffix(
                    pathlib.Path(archive_audio_path).suffix
                )
            ).exists():
                audio_path.write_bytes(info.context["archive_file"].read(archive_audio_path))
        return self


class VOXFactoryAudioViewProperty(BaseModel):
    view: str = "waveform"
    colormap: str = "Heated Metal"
    window: str = "Hann"
    window_size: int = Field(1024, alias="windowSize")
    hop_size: int = Field(256, alias="hopSize")
    f_min: float = Field(27.5, alias="fMin")
    f_max: Optional[float] = Field(None, alias="fMax")
    level_min: Optional[float] = Field(None, alias="levelMin")
    level_max: Optional[float] = Field(None, alias="levelMax")
    level_scale: str = Field("dB", alias="levelScale")
    num_bins: int = Field(230, alias="numBins")
    bins_per_octave: int = Field(24, alias="binsPerOctave")


class VOXFactoryDevice(BaseModel):
    type: str
    track_type: str = Field(alias="trackType")
    name: str
    data: dict[str, Any]
    on: bool


class VOXFactoryTrackBase(BaseModel):
    name: str = ""
    instrument: Optional[str] = None
    h: int = 3
    color: str = "#7878f1"
    volume: float = 1.0
    pan: float = 0.0
    solo: bool = False
    mute: bool = False
    arm: bool = False
    clip_order: list[str] = Field(alias="clipOrder")
    device_bank: dict[str, VOXFactoryDevice] = Field(default_factory=dict, alias="deviceBank")
    device_order: list[str] = Field(default_factory=list, alias="deviceOrder")
    audio_view_property: VOXFactoryAudioViewProperty = Field(
        default_factory=VOXFactoryAudioViewProperty, alias="audioViewProperty"
    )


class VOXFactoryVocalTrack(VOXFactoryTrackBase):
    type: Literal["vocal"] = "vocal"
    clip_bank: dict[str, VOXFactoryVocalClip] = Field(alias="clipBank")


class VOXFactoryAudioTrack(VOXFactoryTrackBase):
    type: Literal["audio"] = "audio"
    clip_bank: dict[str, VOXFactoryAudioClip] = Field(alias="clipBank")


VOXFactoryTrack = Annotated[
    Union[VOXFactoryVocalTrack, VOXFactoryAudioTrack],
    Field(discriminator="type"),
]


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
    metadata: Optional[VOXFactoryMetadata] = None


class VOXFactoryProject(BaseModel):
    version: str = "0.12.0"
    tempo: float
    time_signature: list[int] = Field(alias="timeSignature")
    project_name: str = Field("Untitled Project", alias="projectName")
    track_bank: dict[str, VOXFactoryTrack] = Field(alias="trackBank")
    track_order: list[str] = Field(default_factory=list, alias="trackOrder")
    selected_track_bank: list[str] = Field(default_factory=list, alias="selectedTrackBank")
    selected_clip_bank: list[VOXFactorySelectedClipBankItem] = Field(
        default_factory=list, alias="selectedClipBank"
    )
    selected_note_bank: list[VOXFactorySelectedNoteBankItem] = Field(
        default_factory=list, alias="selectedNoteBank"
    )
    audio_data_bank: dict[str, VOXFactoryAudioData] = Field(
        default_factory=dict, alias="audioDataBank"
    )
