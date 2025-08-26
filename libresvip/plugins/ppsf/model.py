import enum
from typing import Annotated, Any

from pydantic import Field, create_model

from libresvip.model.base import BaseModel
from libresvip.utils.text import uuid_str


class PpsfLanguage(enum.IntEnum):
    _value_: Annotated[
        int,
        create_model(
            "PpsfLanguage",
            __module__="libresvip.plugins.ppsf.model",
            JAPANESE=(int, Field(title="日本語")),
            ENGLISH=(int, Field(title="English")),
            SIMPLIFIED_CHINESE=(int, Field(title="简体中文")),
        ),
    ]
    JAPANESE = 0
    ENGLISH = 1
    SIMPLIFIED_CHINESE = 4


class PpsfCurveType(enum.IntEnum):
    _value_: Annotated[
        int,
        create_model(
            "PpsfCurveType",
            __module__="libresvip.plugins.ppsf.model",
            BORDER=(int, Field(title="Border")),
            NORMAL=(int, Field(title="Normal")),
        ),
    ]
    BORDER = 0
    NORMAL = 1


class PpsfCurvePointSeq(BaseModel):
    border_type: int | None = Field(None, alias="border-type")
    note_index: int | None = Field(None, alias="note-index")
    region_index: int = Field(alias="region-index")
    edited_by_user: bool | None = Field(False, alias="edited-by-user")
    seg_array_id: int | None = Field(None, alias="seg-array-id")
    abs_value: int | None = Field(None, alias="abs-value")


class PpsfCurvePoint(BaseModel):
    plugin_descriptor: str | None = Field(None, alias="plugin-descriptor")
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
    event_index: int | None = None
    length: int | None = None
    muted: bool | None = False
    vibrato_preset_id: int | None = 0
    voice_color_id: int | None = 0
    voice_release_id: int | None = 0
    note_env_preset_id: int | None = 2
    note_gain_value: int | None = 0
    note_param_edited_stats: int | None = 0
    portamento_length: int | None = 180
    portamento_offset: int | None = -120
    vibrato_depth: int | None = 0
    vibrato_rate: int | None = 0
    auto_ai_consonant_length_enabled: bool | None = False
    auto_ai_f0_enabled: bool | None = True
    auto_ai_vibrato_blend_amount: int | None = None
    auto_ai_vibrato_blend_type: int | None = None
    auto_ai_vibrato_default_type: int | None = None
    auto_ai_vibrato_depth: int | None = 0
    auto_ai_vibrato_enabled: bool | None = False
    auto_ai_vibrato_offset: float | None = None
    auto_ai_vibrato_offset_by_user: bool | None = False


class PpsfRegion(BaseModel):
    auto_expand_left: bool | None = Field(None, alias="auto-expand-left")
    auto_expand_right: bool | None = Field(None, alias="auto-expand-right")
    length: int
    muted: bool = False
    name: str = ""
    position: int
    z_order: int = Field(0, alias="z-order")
    audio_event_index: int | None = Field(None, alias="audio-event-index")


class PpsfSubTrack(BaseModel):
    height: int
    plugin_descriptor: str | None = Field(None, alias="plugin-descriptor")
    sub_track_category: int = Field(alias="sub-track-category")
    sub_track_id: int = Field(alias="sub-track-id")


class PpsfParamPoint(BaseModel):
    curve_type: PpsfCurveType = PpsfCurveType.NORMAL
    pos: int
    value: int
    region_index: int | None = Field(None, alias="region-index")
    border_type: int | None = Field(None, alias="border-type")
    note_index: int | None = Field(None, alias="note-index")
    edited_by_user: bool | None = Field(None, alias="edited-by-user")
    seg_array_id: int | None = Field(None, alias="seg-array-id")


class PpsfBaseSequence(BaseModel):
    constant: int
    name: str
    sequence: list[PpsfParamPoint] = Field(default_factory=list)
    use_sequence: bool = False


class PpsfSeqParam(BaseModel):
    base_sequence: PpsfBaseSequence | None = Field(None, alias="base-sequence")
    layers: list[Any] | None = Field(default_factory=list)


class PpsfParameter(PpsfBaseSequence):
    default: int | None = None
    max_value: int | None = Field(None, alias="max")
    min_value: int | None = Field(None, alias="min")


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
    fsm_effects: list[PpsfFsmEffect] | None = Field(default_factory=list, alias="fsm-effects")
    height: int = 64
    index: int
    mute_solo: int = Field(0, alias="mute-solo")
    notes: list[PpsfNote] = Field(default_factory=list)
    nt_envelope_preset_id: int | None = Field(None, alias="nt-envelope-preset-id")
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
    user_markers: list[Any] | None = Field(default_factory=list, alias="user-markers")
    width: int = 1024
    x: int = 100
    y: int = 100


class PpsfLoopPoint(BaseModel):
    begin: int = 0
    enabled: bool | None = Field(False, validation_alias="enable")
    end: int = 7680


class PpsfMetronome(BaseModel):
    enabled: bool | None = Field(False, validation_alias="enable")
    wav: str = "null"


class PpsfGuiSettings(BaseModel):
    loop_point: PpsfLoopPoint | None = Field(default_factory=PpsfLoopPoint)
    metronome: PpsfMetronome | None = Field(default_factory=PpsfMetronome)
    ambient_enabled: bool | None = Field(None, alias="ambient-enabled")
    file_fullpath: str = Field("", alias="file-fullpath")
    playback_position: int = Field(0, alias="playback-position")
    project_length: int = Field(0, alias="project-length")
    track_editor: PpsfTrackEditor = Field(default_factory=PpsfTrackEditor, alias="track-editor")
    auto_connect_interval_msec: int | None = Field(None, alias="auto-connect-interval-msec")
    is_saved_by_nt2: bool | None = Field(None, alias="is-saved-by-nt2")


class PpsfFileAudioData(BaseModel):
    file_path: str = ""
    tempo: int = 0


class PpsfAudioTrackEvent(BaseModel):
    file_audio_data: PpsfFileAudioData
    playback_offset_sample: int = 0
    tick_length: int = 0
    tick_pos: int
    enabled: bool | None = Field(True, validation_alias="enable")


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
    enabled: bool | None = Field(True, validation_alias="enable")
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
    vib_depth: list[PpsfParamPoint] | None = None
    vib_rate: list[PpsfParamPoint] | None = None


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
    library_id: str = Field(default_factory=uuid_str)
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
    return PpsfEnvelope(length=0, offset=0)


class PpsfDvlTrackEvent(BaseModel):
    adjust_speed: bool | None = False
    attack_speed_rate: int = 800000
    consonant_rate: int = 950000
    consonant_speed_rate: int = 1000000
    enabled: bool | None = Field(True, validation_alias="enable")
    length: int
    lyric: str
    note_number: int
    note_off_pit_envelope: PpsfEnvelope | None = Field(default_factory=PpsfEnvelope)
    note_on_pit_envelope: PpsfEnvelope | None = Field(default_factory=PpsfEnvelope)
    portamento_envelope: PpsfEnvelope | None = Field(default_factory=default_portamento_envelope)
    vib_depth: PpsfEnvelope | None = None
    vib_rate: PpsfEnvelope | None = None
    vib_setting_id: int | None = None
    portamento_type: int = 5
    pos: int
    protected: bool = False
    release_speed_rate: int = 1400000
    symbols: str = ""
    vcl_like_note_off: bool | None = False
    is_consonant_length_by_user: bool | None = False

    @property
    def end_pos(self) -> int:
        return self.pos + self.length


class PpsfDvlTrackItem(BaseModel):
    enabled: bool | None = Field(True, validation_alias="enable")
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
    loop_point: PpsfLoopPoint | None = None
    meter: PpsfMeters = Field(default_factory=PpsfMeters)
    metronome: PpsfMetronome | None = None
    name: str = ""
    sampling_rate: int = 48000
    singer_table: list[PpsfSingerTableItem] = Field(default_factory=list)
    tempo: PpsfTempos = Field(default_factory=PpsfTempos)
    vocaloid_track: list[PpsfVocaloidTrackItem] = Field(default_factory=list)
    dvl_track: list[PpsfDvlTrackItem] | None = None


class PpsfRoot(BaseModel):
    app_ver: str = "3.0.0.0"
    gui_settings: PpsfGuiSettings = Field(default_factory=PpsfGuiSettings)
    ppsf_ver: str = "3.2"
    project: PpsfInnerProject = Field(default_factory=PpsfInnerProject)


class PpsfProject(BaseModel):
    ppsf: PpsfRoot = Field(default_factory=PpsfRoot)
