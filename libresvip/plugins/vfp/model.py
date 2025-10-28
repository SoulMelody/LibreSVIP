import pathlib
from typing import Annotated, Any, Literal

from pydantic import Field, ValidationInfo, model_validator
from typing_extensions import Self

from libresvip.model.base import BaseModel


class VoxFactoryVibratoParam(BaseModel):
    start: float = 0
    phase: float = 0
    frequency: float = 5
    amplitude: float = Field(0, alias="amplitude")
    fade_in: float = Field(0, alias="fadeIn")
    fade_out: float = Field(0, alias="fadeOut")


class VoxFactoryGrowlParam(BaseModel):
    start: float = Field(0, alias="start")
    duration: float = Field(0, alias="duration")


class VoxFactoryCorrectionParam(BaseModel):
    modulation: float = Field(0, alias="modulation")
    center: float = Field(0, alias="center")


class VOXFactoryNote(BaseModel):
    time: float
    midi: int
    name: str
    syllable: str
    ticks: float
    duration_ticks: float = Field(alias="durationTicks")
    duration: float = 0.25
    velocity: int = 1
    note_type: str | None = Field(None, alias="noteType")
    vibrato_depth: float | None = Field(None, alias="vibratoDepth")
    pre_bend: float | None = Field(None, alias="preBend")
    post_bend: float | None = Field(None, alias="postBend")
    harmonic_ratio: float | None = Field(None, alias="harmonicRatio")
    pitch_bends: list[float] = Field(default_factory=list, alias="pitchBends")
    vibrato_param: VoxFactoryVibratoParam | None = Field(None, alias="vibratoParam")
    growl_param: VoxFactoryGrowlParam | None = Field(None, alias="growlParam")
    correction_param: VoxFactoryCorrectionParam | None = Field(None, alias="correctionParam")


class VOXFactoryMetadata(BaseModel):
    style: str
    accent: str
    transpose: int
    harmonic_ratio: float = Field(alias="harmonicRatio")
    pitch_detection: str | None = Field(None, alias="pitchDetection")
    instrument: str | None = None


class VOXFactoryClipBase(BaseModel):
    name: str = ""
    start_quarter: float = Field(0, alias="startQuarter")
    offset_quarter: float = Field(0, alias="offsetQuarter")
    length: float
    use_source: bool = Field(True, alias="useSource")
    audio_data_key: str | None = Field(None, alias="audioDataKey")
    audio_data_order: list[str] = Field(default_factory=list, alias="audioDataOrder")
    audio_data_quarter: float = Field(0, alias="audioDataQuarter")
    note_bank: dict[str, VOXFactoryNote] = Field(default_factory=dict, alias="noteBank")
    note_order: list[str] = Field(default_factory=list, alias="noteOrder")
    pitch_point_bank: dict[str, Any] = Field(default_factory=dict, alias="pitchPointBank")
    pitch_point_order: list[str] = Field(default_factory=list, alias="pitchPointOrder")
    next_note_index: int = Field(0, alias="nextNoteIndex")
    pinned_audio_data_order: list[str] = Field(default_factory=list, alias="pinnedAudioDataOrder")
    metadata: VOXFactoryMetadata | None = None
    source_audio_data_key: str | None = Field(None, alias="sourceAudioDataKey")
    process_key: str | None = Field(None, alias="processKey")


class VOXFactoryVocalClip(VOXFactoryClipBase):
    type: Literal["vocal"] = "vocal"
    length_type: Literal["quarter"] = Field("quarter", alias="lengthType")


class VOXFactoryAudioClip(VOXFactoryClipBase):
    type: Literal["audio"] = "audio"
    length_type: Literal["time"] = Field("time", alias="lengthType")

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
                audio_path.write_bytes(
                    (info.context["archive_file"] / archive_audio_path).read_bytes()
                )
        return self


class VOXFactoryAudioViewProperty(BaseModel):
    view: str = "waveform"
    colormap: str = "Heated Metal"
    window: str = "Hann"
    window_size: int = Field(1024, alias="windowSize")
    hop_size: int = Field(256, alias="hopSize")
    f_min: float = Field(27.5, alias="fMin")
    f_max: float | None = Field(None, alias="fMax")
    level_min: float | None = Field(None, alias="levelMin")
    level_max: float | None = Field(None, alias="levelMax")
    level_scale: str = Field("dB", alias="levelScale")
    num_bins: int = Field(230, alias="numBins")
    bins_per_octave: int = Field(24, alias="binsPerOctave")


class VOXFactoryDevice(BaseModel):
    type: str
    track_type: str | None = Field(None, alias="trackType")
    name: str
    data: dict[str, Any] | None = None
    on: bool | None = None
    state: dict[str, Any] | None = None
    params: dict[str, Any] | None = None


class VOXFactoryTrackBase(BaseModel):
    name: str = ""
    instrument: str | None = None
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
    device_preset: str | None = Field(None, alias="devicePreset")
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
    VOXFactoryVocalTrack | VOXFactoryAudioTrack,
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
    metadata: VOXFactoryMetadata | None = None
    pitch_data: list[float] = Field(default_factory=list, alias="pitchData")


class VOXFactoryProject(BaseModel):
    version: str = "0.12.0"
    tempo: float
    time_signature: list[int] = Field(alias="timeSignature")
    loop: list[float] | None = None
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
