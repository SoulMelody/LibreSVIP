import enum
import uuid
from typing import Annotated, Any, Optional

from pydantic import UUID4, Field

from libresvip.model.base import BaseModel


class PpsfLanguage(enum.IntEnum):
    JAPANESE: Annotated[int, Field(title="日本語")] = 0
    ENGLISH: Annotated[int, Field(title="English")] = 1
    SIMPLIFIED_CHINESE: Annotated[int, Field(title="简体中文")] = 4


class PpsfCurveType(enum.IntEnum):
    BORDER: Annotated[int, Field(title="Border")] = 0
    NORMAL: Annotated[int, Field(title="Normal")] = 1


class PpsfMuteflag(enum.IntEnum):
    NONE: Annotated[int, Field(title="None")] = 0
    MUTE: Annotated[int, Field(title="Mute")] = 1
    SOLO: Annotated[int, Field(title="Solo")] = 2


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
    footer_text: str = Field("", alias="footer-text")
    header_text: str = Field("", alias="header-text")
    is_list_end: bool = Field(True, alias="is-list-end")
    is_list_top: bool = Field(True, alias="is-list-top")
    is_word_end: bool = Field(True, alias="is-word-end")
    is_word_top: bool = Field(True, alias="is-word-top")
    lyric_text: str = Field(alias="lyric-text")
    symbols_text: str = Field(alias="symbols-text")


class PpsfNote(BaseModel):
    language: PpsfLanguage = PpsfLanguage.JAPANESE
    region_index: int = Field(alias="region-index")
    syllables: list[PpsfSyllable] = Field(default_factory=list)
    event_index: Optional[int] = None
    length: Optional[int] = None
    muted: Optional[bool] = False
    vibrato_preset_id: Optional[int] = 0
    voice_color_id: Optional[int] = 0
    voice_release_id: Optional[int] = 0
    note_env_preset_id: Optional[int] = 2
    note_gain_value: Optional[int] = 0
    note_param_edited_stats: Optional[int] = 0
    portamento_length: Optional[int] = 180
    portamento_offset: Optional[int] = -120
    vibrato_depth: Optional[int] = 0
    vibrato_rate: Optional[int] = 0


class PpsfRegion(BaseModel):
    auto_expand_left: Optional[bool] = Field(None, alias="auto-expand-left")
    auto_expand_right: Optional[bool] = Field(None, alias="auto-expand-right")
    length: int
    muted: bool = False
    name: str = ""
    position: int
    z_order: int = Field(0, alias="z-order")
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
    use_sequence: bool = False


class PpsfSeqParam(BaseModel):
    base_sequence: Optional[PpsfBaseSequence] = Field(None, alias="base-sequence")
    layers: Optional[list[Any]] = Field(default_factory=list)


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
    curve_points: list[PpsfCurvePoint] = Field(default_factory=list, alias="curve-points")
    fsm_effects: Optional[list[PpsfFsmEffect]] = Field(default_factory=list, alias="fsm-effects")
    height: int = 64
    index: int
    mute_solo: Optional[PpsfMuteflag] = Field(PpsfMuteflag.NONE, alias="mute-solo")
    notes: list[PpsfNote] = Field(default_factory=list)
    nt_envelope_preset_id: Optional[int] = Field(None, alias="nt-envelope-preset-id")
    regions: list[PpsfRegion] = Field(default_factory=list)
    sub_tracks: list[PpsfSubTrack] = Field(default_factory=list, alias="sub-tracks")
    total_height: int = Field(64, alias="total-height")
    track_type: int = Field(alias="track-type")
    vertical_scale: float = Field(1, alias="vertical-scale")
    vertical_scroll: int = Field(0, alias="vertical-scroll")


class PpsfTempoTrack(BaseModel):
    height: int = 0
    vertical_scale: float = Field(2, alias="vertical-scale")
    vertical_scroll: int = Field(0, alias="vertical-scroll")


class PpsfTrackEditor(BaseModel):
    event_tracks: list[PpsfEventTrack] = Field(default_factory=list, alias="event-tracks")
    header_width: int = Field(264, alias="header-width")
    height: int = 720
    horizontal_scale: float = Field(0.08, alias="horizontal-scale")
    horizontal_scroll: int = Field(0, alias="horizontal-scroll")
    tempo_track: PpsfTempoTrack = Field(default_factory=PpsfTempoTrack, alias="tempo-track")
    user_markers: Optional[list[Any]] = Field(default_factory=list, alias="user-markers")
    width: int = 1024
    x: int = 100
    y: int = 100


class PpsfLoopPoint(BaseModel):
    begin: int = 0
    enabled: Optional[bool] = Field(False, validation_alias="enable")
    end: int = 7680


class PpsfMetronome(BaseModel):
    enabled: Optional[bool] = Field(False, validation_alias="enable")
    wav: str = "null"


class PpsfGuiSettings(BaseModel):
    loop_point: Optional[PpsfLoopPoint] = Field(default_factory=PpsfLoopPoint)
    metronome: Optional[PpsfMetronome] = Field(default_factory=PpsfMetronome)
    ambient_enabled: Optional[bool] = Field(None, alias="ambient-enabled")
    file_fullpath: str = Field("", alias="file-fullpath")
    playback_position: int = Field(0, alias="playback-position")
    project_length: int = Field(0, alias="project-length")
    track_editor: PpsfTrackEditor = Field(default_factory=PpsfTrackEditor, alias="track-editor")


class PpsfFileAudioData(BaseModel):
    file_path: str = ""
    tempo: int = 0


class PpsfAudioTrackEvent(BaseModel):
    file_audio_data: PpsfFileAudioData
    playback_offset_sample: int = 0
    tick_length: int = 0
    tick_pos: int
    enabled: Optional[bool] = Field(True, validation_alias="enable")


def default_gain() -> PpsfSeqParam:
    return PpsfSeqParam(
        base_sequence=PpsfBaseSequence(
            constant=750000,
            name="Gain",
        )
    )


def default_panpot() -> PpsfSeqParam:
    return PpsfSeqParam(
        base_sequence=PpsfBaseSequence(
            constant=0,
            name="Panpot",
        )
    )


class PpsfMixer(BaseModel):
    gain: PpsfSeqParam = Field(default_factory=default_gain)
    mixer_type: str = "stereo"
    panpot: PpsfSeqParam = Field(default_factory=default_panpot)


class PpsfAudioTrackItem(BaseModel):
    block_size: int = 279
    enabled: Optional[bool] = Field(True, validation_alias="enable")
    events: list[PpsfAudioTrackEvent] = Field(default_factory=list)
    input_channel: int = 0
    mixer: PpsfMixer = Field(default_factory=PpsfMixer)
    name: str
    output_channel: int = 2
    sampling_rate: int = 48000


class PpsfBaseMeter(BaseModel):
    denomi: int = 4
    nume: int = 4


class PpsfMeter(PpsfBaseMeter):
    measure: int


class PpsfMeters(BaseModel):
    const: PpsfBaseMeter = Field(default_factory=PpsfBaseMeter)
    sequence: list[PpsfMeter] = Field(default_factory=list)
    use_sequence: bool = False


class PpsfSingerParam(BaseModel):
    breathiness: float = 0
    brightness: float = 0
    clearness: float = 0
    gender_factor: float = 0
    opening: float = 0


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
    frame_shift: float = 0.001
    gender: int = 0
    language_id: PpsfLanguage = PpsfLanguage.JAPANESE
    library_id: UUID4 = Field(default_factory=uuid.uuid4)
    name: str = ""
    singer_name: str = "HATSUNE MIKU NT Original"
    stationaly_type: str = "ParamedNDR"
    synthesis_version: str = "V20200915_H"
    tail_silent: float = 0.05
    vprm_morph_mode: str = "Linear"


class PpsfEnvelope(BaseModel):
    length: int = 0
    offset: int = 0
    points: list[PpsfParamPoint] = Field(default_factory=list)
    use_length: bool = True


def default_portamento_envelope() -> PpsfEnvelope:
    return PpsfEnvelope(length=161, offset=-107)


class PpsfDvlTrackEvent(BaseModel):
    adjust_speed: Optional[bool] = False
    attack_speed_rate: int = 800000
    consonant_rate: int = 950000
    consonant_speed_rate: int = 1000000
    enabled: Optional[bool] = Field(True, validation_alias="enable")
    length: int
    lyric: str
    note_number: int
    note_off_pit_envelope: Optional[PpsfEnvelope] = Field(default_factory=PpsfEnvelope)
    note_on_pit_envelope: Optional[PpsfEnvelope] = Field(default_factory=PpsfEnvelope)
    portamento_envelope: Optional[PpsfEnvelope] = Field(default_factory=default_portamento_envelope)
    vib_depth: Optional[PpsfEnvelope] = None
    vib_rate: Optional[PpsfEnvelope] = None
    vib_setting_id: Optional[int] = None
    portamento_type: int = 5
    pos: int
    protected: bool = False
    release_speed_rate: int = 1400000
    symbols: str = ""
    vcl_like_note_off: Optional[bool] = False

    @property
    def end_pos(self) -> int:
        return self.pos + self.length


class PpsfDvlTrackItem(BaseModel):
    enabled: Optional[bool] = Field(True, validation_alias="enable")
    events: list[PpsfDvlTrackEvent] = Field(default_factory=list)
    mixer: PpsfMixer = Field(default_factory=PpsfMixer)
    name: str = "HATSUNE MIKU NT Original"
    parameters: list[PpsfSeqParam] = Field(default_factory=list)
    plugin_output_bus_index: int = 0
    singer: PpsfSinger = Field(default_factory=PpsfSinger)


class PpsfTempo(BaseModel):
    curve_type: PpsfCurveType = PpsfCurveType.NORMAL
    tick: int
    value: int


class PpsfTempos(BaseModel):
    const: int = 1200000
    sequence: list[PpsfTempo] = Field(default_factory=list)
    use_sequence: bool = False


class PpsfInnerProject(BaseModel):
    audio_track: list[PpsfAudioTrackItem] = Field(default_factory=list)
    block_size: int = 279
    loop_point: Optional[PpsfLoopPoint] = None
    meter: PpsfMeters = Field(default_factory=PpsfMeters)
    metronome: Optional[PpsfMetronome] = None
    name: str = ""
    sampling_rate: int = 48000
    singer_table: list[PpsfSingerTableItem] = Field(default_factory=list)
    tempo: PpsfTempos = Field(default_factory=PpsfTempos)
    vocaloid_track: list[PpsfVocaloidTrackItem] = Field(default_factory=list)
    dvl_track: Optional[list[PpsfDvlTrackItem]] = None


class PpsfRoot(BaseModel):
    app_ver: str = "3.0.0.0"
    gui_settings: PpsfGuiSettings = Field(default_factory=PpsfGuiSettings)
    ppsf_ver: str = "3.2"
    project: PpsfInnerProject = Field(default_factory=PpsfInnerProject)


class PpsfProject(BaseModel):
    ppsf: PpsfRoot = Field(default_factory=PpsfRoot)
