import enum
from typing import Annotated, Optional

from pydantic import Field

from libresvip.model.base import BaseModel


class PpsfLanguage(enum.IntEnum):
    JAPANESE: Annotated[int, Field(title="日本語")] = 0
    ENGLISH: Annotated[int, Field(title="English")] = 1
    SIMPLIFIED_CHINESE: Annotated[int, Field(title="简体中文")] = 4


class PpsfCurveType(enum.IntEnum):
    BORDER: Annotated[int, Field(title="Border")] = 0
    NORMAL: Annotated[int, Field(title="Normal")] = 1


class PpsfCurvePointSeq(BaseModel):
    border_type: Optional[int] = Field(None, alias="border-type")
    note_index: Optional[int] = Field(None, alias="note-index")
    region_index: int = Field(alias="region-index")


class PpsfCurvePoint(BaseModel):
    plugin_descriptor: Optional[str] = Field(None, alias="plugin-descriptor")
    sequence: list[PpsfCurvePointSeq] = Field(default_factory=list)
    sub_track_category: int = Field(alias="sub-track-category")
    sub_track_id: int = Field(alias="sub-track-id")


class PpsfSyllable(BaseModel):
    footer_text: str = Field(alias="footer-text")
    header_text: str = Field(alias="header-text")
    is_list_end: bool = Field(alias="is-list-end")
    is_list_top: bool = Field(alias="is-list-top")
    is_word_end: bool = Field(alias="is-word-end")
    is_word_top: bool = Field(alias="is-word-top")
    lyric_text: str = Field(alias="lyric-text")
    symbols_text: str = Field(alias="symbols-text")


class PpsfNote(BaseModel):
    language: PpsfLanguage = PpsfLanguage.JAPANESE
    region_index: int = Field(alias="region-index")
    syllables: list[PpsfSyllable] = Field(default_factory=list)
    event_index: Optional[int] = None
    length: Optional[int] = None
    muted: Optional[bool] = False
    vibrato_preset_id: Optional[int] = None
    voice_color_id: Optional[int] = None
    voice_release_id: Optional[int] = None
    note_env_preset_id: Optional[int] = None
    note_gain_value: Optional[int] = None
    note_param_edited_stats: Optional[int] = None
    portamento_length: Optional[int] = None
    portamento_offset: Optional[int] = None


class PpsfRegion(BaseModel):
    auto_expand_left: Optional[bool] = Field(None, alias="auto-expand-left")
    auto_expand_right: Optional[bool] = Field(None, alias="auto-expand-right")
    length: int
    muted: bool = False
    name: str
    position: int
    z_order: int = Field(alias="z-order")
    audio_event_index: Optional[int] = Field(None, alias="audio-event-index")


class PpsfSubTrack(BaseModel):
    height: int
    plugin_descriptor: Optional[str] = Field(None, alias="plugin-descriptor")
    sub_track_category: int = Field(alias="sub-track-category")
    sub_track_id: int = Field(alias="sub-track-id")


class PpsfParamPoint(BaseModel):
    curve_type: PpsfCurveType = PpsfCurveType.NORMAL
    pos: int
    value: int
    region_index: Optional[int] = Field(None, alias="region-index")


class PpsfBaseSequence(BaseModel):
    constant: int
    name: str
    sequence: list[PpsfParamPoint] = Field(default_factory=list)
    use_sequence: bool


class PpsfSeqParam(BaseModel):
    base_sequence: Optional[PpsfBaseSequence] = Field(None, alias="base-sequence")
    layers: Optional[list] = None


class PpsfParameter(PpsfBaseSequence):
    default: Optional[int] = None
    max_value: Optional[int] = Field(None, alias="max")
    min_value: Optional[int] = Field(None, alias="min")


class PpsfFsmEffect(BaseModel):
    parameters: list[PpsfParameter] = Field(default_factory=list)
    plugin_id: int = Field(alias="plugin-id")
    plugin_name: str = Field(alias="plugin-name")
    power_state: bool = Field(alias="power-state")
    program_name: str = Field(alias="program-name")
    program_number: int = Field(alias="program-number")
    version: str


class PpsfEventTrack(BaseModel):
    curve_points: list[PpsfCurvePoint] = Field(
        default_factory=list, alias="curve-points"
    )
    fsm_effects: Optional[list[PpsfFsmEffect]] = Field(None, alias="fsm-effects")
    height: int
    index: int
    mute_solo: Optional[int] = Field(None, alias="mute-solo")
    notes: Optional[list[PpsfNote]] = Field(default_factory=list)
    nt_envelope_preset_id: Optional[int] = Field(None, alias="nt-envelope-preset-id")
    regions: list[PpsfRegion] = Field(default_factory=list)
    sub_tracks: list[PpsfSubTrack] = Field(default_factory=list, alias="sub-tracks")
    total_height: int = Field(alias="total-height")
    track_type: int = Field(alias="track-type")
    vertical_scale: int = Field(alias="vertical-scale")
    vertical_scroll: int = Field(alias="vertical-scroll")


class PpsfTempoTrack(BaseModel):
    height: int
    vertical_scale: int = Field(alias="vertical-scale")
    vertical_scroll: int = Field(alias="vertical-scroll")


class PpsfTrackEditor(BaseModel):
    event_tracks: list[PpsfEventTrack] = Field(
        default_factory=list, alias="event-tracks"
    )
    header_width: int = Field(alias="header-width")
    height: int
    horizontal_scale: float = Field(alias="horizontal-scale")
    horizontal_scroll: int = Field(alias="horizontal-scroll")
    tempo_track: PpsfTempoTrack = Field(alias="tempo-track")
    user_markers: Optional[list] = Field(default_factory=list, alias="user-markers")
    width: int
    x: int
    y: int


class PpsfLoopPoint(BaseModel):
    begin: int
    enabled: Optional[bool] = Field(None, validation_alias="enable")
    end: int


class PpsfMetronome(BaseModel):
    enabled: Optional[bool] = Field(None, validation_alias="enable")
    wav: str


class PpsfGuiSettings(BaseModel):
    loop_point: Optional[PpsfLoopPoint] = None
    metronome: Optional[PpsfMetronome] = None
    ambient_enabled: Optional[bool] = Field(None, alias="ambient-enabled")
    file_fullpath: str = Field(alias="file-fullpath")
    playback_position: int = Field(alias="playback-position")
    project_length: int = Field(alias="project-length")
    track_editor: PpsfTrackEditor = Field(
        default_factory=PpsfTrackEditor, alias="track-editor"
    )


class PpsfFileAudioData(BaseModel):
    file_path: str
    tempo: int


class PpsfAudioTrackEvent(BaseModel):
    file_audio_data: PpsfFileAudioData = Field(default_factory=PpsfFileAudioData)
    playback_offset_sample: int
    tick_length: int
    tick_pos: int
    enabled: Optional[bool] = Field(None, validation_alias="enable")


class PpsfMixer(BaseModel):
    gain: PpsfSeqParam = Field(default_factory=PpsfSeqParam)
    mixer_type: str
    panpot: PpsfSeqParam = Field(default_factory=PpsfSeqParam)


class PpsfAudioTrackItem(BaseModel):
    block_size: int = 512
    enabled: Optional[bool] = Field(None, validation_alias="enable")
    events: list[PpsfAudioTrackEvent] = Field(default_factory=list)
    input_channel: int = 0
    mixer: PpsfMixer = Field(default_factory=PpsfMixer)
    name: str
    output_channel: int = 2
    sampling_rate: int = 44100


class PpsfMeter(BaseModel):
    measure: Optional[int] = None
    denomi: int
    nume: int


class PpsfMeters(BaseModel):
    const: PpsfMeter = Field(default_factory=PpsfMeter)
    sequence: list[PpsfMeter] = Field(default_factory=list)
    use_sequence: bool


class PpsfSingerParam(BaseModel):
    breathiness: int
    brightness: int
    clearness: int
    gender_factor: int
    opening: int


class PpsfSingerTableItem(BaseModel):
    cid1: str
    name: str
    param1: PpsfSingerParam = Field(default_factory=PpsfSingerParam)


class PpsfVocaloidTrackEvent(BaseModel):
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
    vib_depth: Optional[list[PpsfParamPoint]] = None
    vib_rate: Optional[list[PpsfParamPoint]] = None


class PpsfVocaloidTrackItem(BaseModel):
    events: list[PpsfVocaloidTrackEvent] = Field(default_factory=list)
    mixer: PpsfMixer = Field(default_factory=PpsfMixer)
    name: str
    parameters: list[PpsfParameter] = Field(default_factory=list)
    singer: int


class PpsfSinger(BaseModel):
    character_name: str = "miku"
    do_extrapolation: bool = False
    frame_shift: float = 0.003
    gender: int = 0
    language_id: PpsfLanguage = PpsfLanguage.JAPANESE
    library_id: str
    name: str = ""
    singer_name: str = "HATSUNE MIKU NT"
    stationaly_type: str = "ParamedNDR"
    synthesis_version: str
    tail_silent: float = 0.05
    vprm_morph_mode: str = "Linear"


class PpsfEnvelope(BaseModel):
    length: int
    offset: int
    points: list[PpsfParamPoint] = Field(default_factory=list)
    use_length: bool


class PpsfDvlTrackEvent(BaseModel):
    adjust_speed: Optional[bool] = None
    attack_speed_rate: int
    consonant_rate: int
    consonant_speed_rate: int
    enabled: Optional[bool] = Field(True, validation_alias="enable")
    length: int
    lyric: str
    note_number: int
    note_off_pit_envelope: Optional[PpsfEnvelope] = None
    note_on_pit_envelope: Optional[PpsfEnvelope] = None
    portamento_envelope: Optional[PpsfEnvelope] = None
    vib_depth: Optional[PpsfEnvelope] = None
    vib_rate: Optional[PpsfEnvelope] = None
    vib_setting_id: Optional[int] = None
    portamento_type: int
    pos: int
    protected: bool
    release_speed_rate: int
    symbols: str
    vcl_like_note_off: Optional[bool] = None


class PpsfDvlTrackItem(BaseModel):
    enabled: Optional[bool] = Field(None, validation_alias="enable")
    events: list[PpsfDvlTrackEvent] = Field(default_factory=list)
    mixer: PpsfMixer = Field(default_factory=PpsfMixer)
    name: str
    parameters: list[PpsfSeqParam] = Field(default_factory=list)
    plugin_output_bus_index: int
    singer: PpsfSinger = Field(default_factory=PpsfSinger)


class PpsfTempo(BaseModel):
    curve_type: PpsfCurveType = PpsfCurveType.NORMAL
    tick: int
    value: int


class PpsfTempos(BaseModel):
    const: int
    sequence: list[PpsfTempo] = Field(default_factory=list)
    use_sequence: bool


class PpsfInnerProject(BaseModel):
    audio_track: list[PpsfAudioTrackItem] = Field(default_factory=list)
    block_size: int = 512
    loop_point: Optional[PpsfLoopPoint] = None
    meter: PpsfMeters = Field(default_factory=PpsfMeters)
    metronome: Optional[PpsfMetronome] = None
    name: str
    sampling_rate: int = 44100
    singer_table: list[PpsfSingerTableItem] = Field(default_factory=list)
    tempo: PpsfTempos = Field(default_factory=PpsfTempos)
    vocaloid_track: list[PpsfVocaloidTrackItem] = Field(default_factory=list)
    dvl_track: Optional[list[PpsfDvlTrackItem]] = None


class PpsfRoot(BaseModel):
    app_ver: str = "3.0.0.0"
    gui_settings: PpsfGuiSettings = Field(default_factory=PpsfGuiSettings)
    ppsf_ver: str = "3.0"
    project: PpsfInnerProject = Field(default_factory=PpsfInnerProject)


class PpsfProject(BaseModel):
    ppsf: PpsfRoot = Field(default_factory=PpsfRoot)
