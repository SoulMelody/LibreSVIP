from typing import List, Optional

from pydantic import Field

from libresvip.model.base import BaseModel


class SequenceItem(BaseModel):
    region_index: int = Field(..., alias="region-index")


class CurvePoint(BaseModel):
    plugin_descriptor: str = Field(..., alias="plugin-descriptor")
    sequence: List[SequenceItem]
    sub_track_category: int = Field(..., alias="sub-track-category")
    sub_track_id: int = Field(..., alias="sub-track-id")


class Syllable(BaseModel):
    footer_text: str = Field(..., alias="footer-text")
    header_text: str = Field(..., alias="header-text")
    is_list_end: bool = Field(..., alias="is-list-end")
    is_list_top: bool = Field(..., alias="is-list-top")
    is_word_end: bool = Field(..., alias="is-word-end")
    is_word_top: bool = Field(..., alias="is-word-top")
    lyric_text: str = Field(..., alias="lyric-text")
    symbols_text: str = Field(..., alias="symbols-text")


class Note(BaseModel):
    evec: List
    language: int
    region_index: int = Field(..., alias="region-index")
    syllables: List[Syllable]


class Region(BaseModel):
    auto_expand_left: Optional[bool] = Field(None, alias="auto-expand-left")
    auto_expand_right: Optional[bool] = Field(None, alias="auto-expand-right")
    length: int
    muted: bool
    name: str
    position: int
    z_order: int = Field(..., alias="z-order")
    audio_event_index: Optional[int] = Field(None, alias="audio-event-index")


class SubTrack(BaseModel):
    height: int
    plugin_descriptor: str = Field(..., alias="plugin-descriptor")
    sub_track_category: int = Field(..., alias="sub-track-category")
    sub_track_id: int = Field(..., alias="sub-track-id")


class EventTrack(BaseModel):
    curve_points: List[CurvePoint] = Field(..., alias="curve-points")
    height: int
    index: int
    notes: Optional[List[Note]] = None
    regions: List[Region]
    sub_tracks: List[SubTrack] = Field(..., alias="sub-tracks")
    total_height: int = Field(..., alias="total-height")
    track_type: int = Field(..., alias="track-type")
    vertical_scale: int = Field(..., alias="vertical-scale")
    vertical_scroll: int = Field(..., alias="vertical-scroll")


class TempoTrack(BaseModel):
    height: int
    vertical_scale: int = Field(..., alias="vertical-scale")
    vertical_scroll: int = Field(..., alias="vertical-scroll")


class TrackEditor(BaseModel):
    event_tracks: List[EventTrack] = Field(..., alias="event-tracks")
    header_width: int = Field(..., alias="header-width")
    height: int
    horizontal_scale: float = Field(..., alias="horizontal-scale")
    horizontal_scroll: int = Field(..., alias="horizontal-scroll")
    tempo_track: TempoTrack = Field(..., alias="tempo-track")
    width: int
    x: int
    y: int


class GuiSettings(BaseModel):
    ambient_enabled: bool = Field(..., alias="ambient-enabled")
    file_fullpath: str = Field(..., alias="file-fullpath")
    playback_position: int = Field(..., alias="playback-position")
    project_length: int = Field(..., alias="project-length")
    track_editor: TrackEditor = Field(..., alias="track-editor")


class FileAudioData(BaseModel):
    file_path: str
    tempo: int


class Event(BaseModel):
    file_audio_data: FileAudioData
    playback_offset_sample: int
    tick_length: int
    tick_pos: int


class Gain(BaseModel):
    constant: int
    sequence: List
    use_sequence: bool


class Panpot(BaseModel):
    constant: int
    sequence: List
    use_sequence: bool


class Mixer(BaseModel):
    gain: Gain
    mixer_type: str
    panpot: Panpot


class AudioTrackItem(BaseModel):
    block_size: int
    enabled: bool
    events: List[Event]
    input_channel: int
    mixer: Mixer
    name: str
    output_channel: int
    sampling_rate: int


class LoopPoint(BaseModel):
    begin: int
    enable: bool
    end: int


class Const(BaseModel):
    denomi: int
    nume: int


class Meter(BaseModel):
    const: Const
    use_sequence: bool


class Metronome(BaseModel):
    enable: bool
    wav: str


class Param1(BaseModel):
    breathiness: int
    brightness: int
    clearness: int
    gender_factor: int
    opening: int


class SingerTableItem(BaseModel):
    cid1: str
    name: str
    param1: Param1


class Tempo(BaseModel):
    const: int
    use_sequence: bool


class VibDepthItem(BaseModel):
    curve_type: int
    pos: int
    value: int


class VibRateItem(BaseModel):
    curve_type: int
    pos: int
    value: int


class Event1(BaseModel):
    accent: int
    bend_depth: int
    bend_length: int
    decay: int
    fall_port: bool
    length: int
    lyric: str
    note_number: int
    opening: int
    pos: int
    protected: bool
    rise_port: bool
    symbols: str
    velocity: int
    vib_category: int
    vib_offset: int
    vib_depth: Optional[List[VibDepthItem]] = None
    vib_rate: Optional[List[VibRateItem]] = None


class SequenceItem1(BaseModel):
    curve_type: int
    pos: int
    value: int


class Parameter(BaseModel):
    constant: int
    default: int
    max: int
    min: int
    name: str
    sequence: List[SequenceItem1]
    use_sequence: bool


class VocaloidTrackItem(BaseModel):
    events: List[Event1]
    mixer: Mixer
    name: str
    parameters: List[Parameter]
    singer: int


class PpsfInnerProject(BaseModel):
    audio_track: List[AudioTrackItem]
    block_size: int
    loop_point: LoopPoint
    meter: Meter
    metronome: Metronome
    name: str
    sampling_rate: int
    singer_table: List[SingerTableItem]
    tempo: Tempo
    vocaloid_track: List[VocaloidTrackItem]


class PpsfRoot(BaseModel):
    app_ver: str
    gui_settings: GuiSettings
    ppsf_ver: str
    project: PpsfInnerProject


class PpsfProject(BaseModel):
    ppsf: PpsfRoot
