import abc

from pydantic import BaseModel
from xsdata_pydantic.fields import field


class VibratoBPList(abc.ABC, BaseModel):
    data: str = field(
        metadata={
            "name": "Data",
            "type": "Element",
            "required": True,
        }
    )


class VsqBPList(VibratoBPList):
    default: int = field(
        metadata={
            "name": "Default",
            "type": "Element",
            "required": True,
        }
    )
    name: str = field(
        metadata={
            "name": "Name",
            "type": "Element",
            "required": True,
        }
    )
    maximum: int = field(
        metadata={
            "name": "Maximum",
            "type": "Element",
            "required": True,
        }
    )
    minimum: int = field(
        metadata={
            "name": "Minimum",
            "type": "Element",
            "required": True,
        }
    )


class PointD(BaseModel):
    x: float = field(
        metadata={
            "name": "X",
            "type": "Element",
            "required": True,
        }
    )
    y: float = field(
        metadata={
            "name": "Y",
            "type": "Element",
            "required": True,
        }
    )


class BgmFile(BaseModel):
    file: str = field(
        metadata={
            "type": "Element",
            "required": True,
        }
    )
    feder: int = field(
        metadata={
            "type": "Element",
            "required": True,
        }
    )
    panpot: int = field(
        metadata={
            "type": "Element",
            "required": True,
        }
    )
    mute: int = field(
        metadata={
            "type": "Element",
            "required": True,
        }
    )
    start_after_premeasure: bool = field(
        metadata={
            "name": "startAfterPremeasure",
            "type": "Element",
            "required": True,
        }
    )
    read_offset_seconds: int = field(
        metadata={
            "name": "readOffsetSeconds",
            "type": "Element",
            "required": True,
        }
    )


class VsqCommon(BaseModel):
    version: str = field(
        metadata={
            "name": "Version",
            "type": "Element",
            "required": True,
        }
    )
    name: str = field(
        metadata={
            "name": "Name",
            "type": "Element",
            "required": True,
        }
    )
    color: str = field(
        metadata={
            "name": "Color",
            "type": "Element",
            "required": True,
        }
    )
    dynamics_mode: int = field(
        metadata={
            "name": "DynamicsMode",
            "type": "Element",
            "required": True,
        }
    )
    play_mode: int = field(
        metadata={
            "name": "PlayMode",
            "type": "Element",
            "required": True,
        }
    )
    last_play_mode: int = field(
        metadata={
            "name": "LastPlayMode",
            "type": "Element",
            "required": True,
        }
    )


class IconHandle(BaseModel):
    caption: str = field(
        metadata={
            "name": "Caption",
            "type": "Element",
            "required": True,
        }
    )
    icon_id: str = field(
        metadata={
            "name": "IconID",
            "type": "Element",
            "required": True,
        }
    )
    ids: str = field(
        metadata={
            "name": "IDS",
            "type": "Element",
            "required": True,
        }
    )
    index: int = field(
        metadata={
            "name": "Index",
            "type": "Element",
            "required": True,
        }
    )
    length: int = field(
        metadata={
            "name": "Length",
            "type": "Element",
            "required": True,
        }
    )
    original: int = field(
        metadata={
            "name": "Original",
            "type": "Element",
            "required": True,
        }
    )
    program: int = field(
        metadata={
            "name": "Program",
            "type": "Element",
            "required": True,
        }
    )
    language: int = field(
        metadata={
            "name": "Language",
            "type": "Element",
            "required": True,
        }
    )


class Lyric(BaseModel):
    phrase: str | None = field(
        default=None,
        metadata={
            "name": "Phrase",
            "type": "Element",
        },
    )
    unknown_float: float | None = field(
        default=None,
        metadata={
            "name": "UnknownFloat",
            "type": "Element",
        },
    )
    phonetic_symbol_protected: bool | None = field(
        default=None,
        metadata={
            "name": "PhoneticSymbolProtected",
            "type": "Element",
        },
    )
    consonant_adjustment: int | str | None = field(
        default=None,
        metadata={
            "name": "ConsonantAdjustment",
            "type": "Element",
        },
    )
    phonetic_symbol: str | None = field(
        default=None,
        metadata={
            "name": "PhoneticSymbol",
            "type": "Element",
        },
    )


class VsqMaster(BaseModel):
    pre_measure: int = field(
        metadata={
            "name": "PreMeasure",
            "type": "Element",
            "required": True,
        }
    )


class NoteHeadHandle(BaseModel):
    index: int = field(
        metadata={
            "name": "Index",
            "type": "Element",
            "required": True,
        }
    )
    icon_id: str = field(
        metadata={
            "name": "IconID",
            "type": "Element",
            "required": True,
        }
    )
    ids: str = field(
        metadata={
            "name": "IDS",
            "type": "Element",
            "required": True,
        }
    )
    original: int = field(
        metadata={
            "name": "Original",
            "type": "Element",
            "required": True,
        }
    )
    depth: int = field(
        metadata={
            "name": "Depth",
            "type": "Element",
            "required": True,
        }
    )
    duration: int = field(
        metadata={
            "name": "Duration",
            "type": "Element",
            "required": True,
        }
    )
    caption: str = field(
        metadata={
            "name": "Caption",
            "type": "Element",
            "required": True,
        }
    )
    length: int = field(
        metadata={
            "name": "Length",
            "type": "Element",
            "required": True,
        }
    )


class TempoTableEntry(BaseModel):
    clock: int = field(
        metadata={
            "name": "Clock",
            "type": "Element",
            "required": True,
        }
    )
    tempo: int = field(
        metadata={
            "name": "Tempo",
            "type": "Element",
            "required": True,
        }
    )
    time: int = field(
        metadata={
            "name": "Time",
            "type": "Element",
            "required": True,
        }
    )


class TimeSigTableEntry(BaseModel):
    clock: int = field(
        metadata={
            "name": "Clock",
            "type": "Element",
            "required": True,
        }
    )
    numerator: int = field(
        metadata={
            "name": "Numerator",
            "type": "Element",
            "required": True,
        }
    )
    denominator: int = field(
        metadata={
            "name": "Denominator",
            "type": "Element",
            "required": True,
        }
    )
    bar_count: int = field(
        metadata={
            "name": "BarCount",
            "type": "Element",
            "required": True,
        }
    )


class UstEventProperty(BaseModel):
    name: str | None = field(
        default=None,
        metadata={
            "name": "Name",
            "type": "Element",
        },
    )
    value: str | None = field(
        default=None,
        metadata={
            "name": "Value",
            "type": "Element",
        },
    )


class UstEvent(BaseModel):
    flags: str | None = field(
        default=None,
        metadata={
            "name": "Flags",
            "type": "Element",
        },
    )
    index: int = field(
        metadata={
            "name": "Index",
            "type": "Element",
            "required": True,
        }
    )
    properties: list[UstEventProperty] = field(
        default_factory=list,
        metadata={
            "name": "Properties",
            "type": "Element",
        },
    )
    lyric: str | None = field(
        default=None,
        metadata={
            "name": "Lyric",
            "type": "Element",
        },
    )
    note: int = field(
        metadata={
            "name": "Note",
            "type": "Element",
            "required": True,
        }
    )
    intensity: int = field(
        metadata={
            "name": "Intensity",
            "type": "Element",
            "required": True,
        }
    )
    pbtype: int = field(
        metadata={
            "name": "PBType",
            "type": "Element",
            "required": True,
        }
    )
    tempo: int = field(
        metadata={
            "name": "Tempo",
            "type": "Element",
            "required": True,
        }
    )
    pre_utterance: int = field(
        metadata={
            "name": "PreUtterance",
            "type": "Element",
            "required": True,
        }
    )
    voice_overlap: int = field(
        metadata={
            "name": "VoiceOverlap",
            "type": "Element",
            "required": True,
        }
    )
    moduration: int = field(
        metadata={
            "name": "Moduration",
            "type": "Element",
            "required": True,
        }
    )
    start_point: int = field(
        metadata={
            "name": "StartPoint",
            "type": "Element",
            "required": True,
        }
    )
    length: int = field(
        metadata={
            "name": "Length",
            "type": "Element",
            "required": True,
        }
    )


class VsqMixerEntry(BaseModel):
    feder: int = field(
        metadata={
            "name": "Feder",
            "type": "Element",
            "required": True,
        }
    )
    panpot: int = field(
        metadata={
            "name": "Panpot",
            "type": "Element",
            "required": True,
        }
    )
    mute: int = field(
        metadata={
            "name": "Mute",
            "type": "Element",
            "required": True,
        }
    )
    solo: int = field(
        metadata={
            "name": "Solo",
            "type": "Element",
            "required": True,
        }
    )


class SequenceConfig(BaseModel):
    class Meta:
        name = "config"

    sampling_rate: int = field(
        metadata={
            "name": "SamplingRate",
            "type": "Element",
            "required": True,
        }
    )
    wave_file_output_channel: int = field(
        metadata={
            "name": "WaveFileOutputChannel",
            "type": "Element",
            "required": True,
        }
    )
    wave_file_output_from_master_track: bool = field(
        metadata={
            "name": "WaveFileOutputFromMasterTrack",
            "type": "Element",
            "required": True,
        }
    )
    start_marker: int = field(
        metadata={
            "name": "StartMarker",
            "type": "Element",
            "required": True,
        }
    )
    start_marker_enabled: bool = field(
        metadata={
            "name": "StartMarkerEnabled",
            "type": "Element",
            "required": True,
        }
    )
    end_marker: int = field(
        metadata={
            "name": "EndMarker",
            "type": "Element",
            "required": True,
        }
    )
    end_marker_enabled: bool = field(
        metadata={
            "name": "EndMarkerEnabled",
            "type": "Element",
            "required": True,
        }
    )


class BezierPoint(BaseModel):
    base: PointD = field(
        metadata={
            "name": "Base",
            "type": "Element",
            "required": True,
        }
    )
    control_left: PointD = field(
        metadata={
            "name": "ControlLeft",
            "type": "Element",
            "required": True,
        }
    )
    control_right: PointD = field(
        metadata={
            "name": "ControlRight",
            "type": "Element",
            "required": True,
        }
    )
    control_left_type: str = field(
        metadata={
            "name": "ControlLeftType",
            "type": "Element",
            "required": True,
        }
    )
    control_right_type: str = field(
        metadata={
            "name": "ControlRightType",
            "type": "Element",
            "required": True,
        }
    )


class BgmFiles(BaseModel):
    bgm_file: BgmFile = field(
        metadata={
            "name": "BgmFile",
            "type": "Element",
            "required": True,
        }
    )


class IconDynamicsHandle(BaseModel):
    icon_id: str = field(
        metadata={
            "name": "IconID",
            "type": "Element",
            "required": True,
        }
    )
    ids: str = field(
        metadata={
            "name": "IDS",
            "type": "Element",
            "required": True,
        }
    )
    original: int = field(
        metadata={
            "name": "Original",
            "type": "Element",
            "required": True,
        }
    )
    caption: str = field(
        metadata={
            "name": "Caption",
            "type": "Element",
            "required": True,
        }
    )
    length: int = field(
        metadata={
            "name": "Length",
            "type": "Element",
            "required": True,
        }
    )
    start_dyn: int = field(
        metadata={
            "name": "StartDyn",
            "type": "Element",
            "required": True,
        }
    )
    end_dyn: int = field(
        metadata={
            "name": "EndDyn",
            "type": "Element",
            "required": True,
        }
    )
    dyn_bp: VibratoBPList = field(
        metadata={
            "name": "DynBP",
            "type": "Element",
            "required": True,
        }
    )


class Slave(BaseModel):
    vsq_mixer_entry: list[VsqMixerEntry] = field(
        default_factory=list,
        metadata={
            "name": "VsqMixerEntry",
            "type": "Element",
            "min_occurs": 1,
        },
    )


class TempoTable(BaseModel):
    tempo_table_entry: list[TempoTableEntry] = field(
        default_factory=list,
        metadata={
            "name": "TempoTableEntry",
            "type": "Element",
            "min_occurs": 1,
        },
    )


class TimesigTable(BaseModel):
    time_sig_table_entry: list[TimeSigTableEntry] = field(
        default_factory=list,
        metadata={
            "name": "TimeSigTableEntry",
            "type": "Element",
            "min_occurs": 1,
        },
    )


class Trailing(BaseModel):
    lyric: Lyric | None = field(
        default=None,
        metadata={
            "name": "Lyric",
            "type": "Element",
        },
    )


class VibratoHandle(BaseModel):
    index: int = field(
        metadata={
            "name": "Index",
            "type": "Element",
            "required": True,
        }
    )
    icon_id: str = field(
        metadata={
            "name": "IconID",
            "type": "Element",
            "required": True,
        }
    )
    ids: str = field(
        metadata={
            "name": "IDS",
            "type": "Element",
            "required": True,
        }
    )
    original: int = field(
        metadata={
            "name": "Original",
            "type": "Element",
            "required": True,
        }
    )
    caption: str = field(
        metadata={
            "name": "Caption",
            "type": "Element",
            "required": True,
        }
    )
    rate_bp: VibratoBPList = field(
        metadata={
            "name": "RateBP",
            "type": "Element",
            "required": True,
        }
    )
    start_rate: int = field(
        metadata={
            "name": "StartRate",
            "type": "Element",
            "required": True,
        }
    )
    depth_bp: VibratoBPList = field(
        metadata={
            "name": "DepthBP",
            "type": "Element",
            "required": True,
        }
    )
    start_depth: int = field(
        metadata={
            "name": "StartDepth",
            "type": "Element",
            "required": True,
        }
    )
    length: int = field(
        metadata={
            "name": "Length",
            "type": "Element",
            "required": True,
        }
    )


class LyricHandle(BaseModel):
    l0: Lyric = field(
        metadata={
            "name": "L0",
            "type": "Element",
            "required": True,
        }
    )
    index: int = field(
        metadata={
            "name": "Index",
            "type": "Element",
            "required": True,
        }
    )
    trailing: Trailing = field(
        metadata={
            "name": "Trailing",
            "type": "Element",
            "required": True,
        }
    )


class VsqMixer(BaseModel):
    master_feder: int = field(
        metadata={
            "name": "MasterFeder",
            "type": "Element",
            "required": True,
        }
    )
    master_panpot: int = field(
        metadata={
            "name": "MasterPanpot",
            "type": "Element",
            "required": True,
        }
    )
    master_mute: int = field(
        metadata={
            "name": "MasterMute",
            "type": "Element",
            "required": True,
        }
    )
    output_mode: int = field(
        metadata={
            "name": "OutputMode",
            "type": "Element",
            "required": True,
        }
    )
    slave: Slave = field(
        metadata={
            "name": "Slave",
            "type": "Element",
            "required": True,
        }
    )


class Points(BaseModel):
    class Meta:
        name = "points"

    bezier_point: list[BezierPoint] = field(
        default_factory=list,
        metadata={
            "name": "BezierPoint",
            "type": "Element",
            "min_occurs": 1,
        },
    )


class BezierChain(BaseModel):
    points: Points = field(
        metadata={
            "type": "Element",
            "required": True,
        }
    )
    default: int = field(
        metadata={
            "name": "Default",
            "type": "Element",
            "required": True,
        }
    )
    id: int = field(
        metadata={
            "type": "Element",
            "required": True,
        }
    )


class BezierChainList(BaseModel):
    bezier_chain: BezierChain | None = field(
        default=None,
        metadata={
            "name": "BezierChain",
            "type": "Element",
        },
    )


class VsqID(BaseModel):
    class Meta:
        name = "ID"

    type_value: str = field(
        metadata={
            "name": "type",
            "type": "Element",
            "required": True,
        }
    )
    icon_handle: IconHandle | None = field(
        default=None,
        metadata={
            "name": "IconHandle",
            "type": "Element",
        },
    )
    note: int = field(
        metadata={
            "name": "Note",
            "type": "Element",
            "required": True,
        }
    )
    dynamics: int = field(
        metadata={
            "name": "Dynamics",
            "type": "Element",
            "required": True,
        }
    )
    pmbend_depth: int = field(
        metadata={
            "name": "PMBendDepth",
            "type": "Element",
            "required": True,
        }
    )
    pmbend_length: int = field(
        metadata={
            "name": "PMBendLength",
            "type": "Element",
            "required": True,
        }
    )
    pmb_portamento_use: int = field(
        metadata={
            "name": "PMbPortamentoUse",
            "type": "Element",
            "required": True,
        }
    )
    demdec_gain_rate: int = field(
        metadata={
            "name": "DEMdecGainRate",
            "type": "Element",
            "required": True,
        }
    )
    demaccent: int = field(
        metadata={
            "name": "DEMaccent",
            "type": "Element",
            "required": True,
        }
    )
    lyric_handle: LyricHandle | None = field(
        default=None,
        metadata={
            "name": "LyricHandle",
            "type": "Element",
        },
    )
    vibrato_handle: VibratoHandle | None = field(
        default=None,
        metadata={
            "name": "VibratoHandle",
            "type": "Element",
        },
    )
    vibrato_delay: int = field(
        metadata={
            "name": "VibratoDelay",
            "type": "Element",
            "required": True,
        }
    )
    note_head_handle: NoteHeadHandle | None = field(
        default=None,
        metadata={
            "name": "NoteHeadHandle",
            "type": "Element",
        },
    )
    p_mean_onset_first_note: int = field(
        metadata={
            "name": "pMeanOnsetFirstNote",
            "type": "Element",
            "required": True,
        }
    )
    v_mean_note_transition: int = field(
        metadata={
            "name": "vMeanNoteTransition",
            "type": "Element",
            "required": True,
        }
    )
    d4mean: int = field(
        metadata={
            "type": "Element",
            "required": True,
        }
    )
    p_mean_ending_note: int = field(
        metadata={
            "name": "pMeanEndingNote",
            "type": "Element",
            "required": True,
        }
    )
    icon_dynamics_handle: IconDynamicsHandle | None = field(
        default=None,
        metadata={
            "name": "IconDynamicsHandle",
            "type": "Element",
        },
    )
    length: int = field(
        metadata={
            "name": "Length",
            "type": "Element",
            "required": True,
        }
    )


class VsqEvent(BaseModel):
    internal_id: int = field(
        metadata={
            "name": "InternalID",
            "type": "Element",
            "required": True,
        }
    )
    clock: int = field(
        metadata={
            "name": "Clock",
            "type": "Element",
            "required": True,
        }
    )
    id: VsqID = field(
        metadata={
            "name": "ID",
            "type": "Element",
            "required": True,
        }
    )
    ust_event: UstEvent = field(
        metadata={
            "name": "UstEvent",
            "type": "Element",
            "required": True,
        }
    )


class BezierCurves(BaseModel):
    dynamics: BezierChainList = field(
        metadata={
            "name": "Dynamics",
            "type": "Element",
            "required": True,
        }
    )
    brethiness: BezierChainList = field(
        metadata={
            "name": "Brethiness",
            "type": "Element",
            "required": True,
        }
    )
    brightness: BezierChainList = field(
        metadata={
            "name": "Brightness",
            "type": "Element",
            "required": True,
        }
    )
    clearness: BezierChainList = field(
        metadata={
            "name": "Clearness",
            "type": "Element",
            "required": True,
        }
    )
    opening: BezierChainList = field(
        metadata={
            "name": "Opening",
            "type": "Element",
            "required": True,
        }
    )
    gender_factor: BezierChainList = field(
        metadata={
            "name": "GenderFactor",
            "type": "Element",
            "required": True,
        }
    )
    portamento_timing: BezierChainList = field(
        metadata={
            "name": "PortamentoTiming",
            "type": "Element",
            "required": True,
        }
    )
    vibrato_rate: BezierChainList | None = field(
        default=None,
        metadata={
            "name": "VibratoRate",
            "type": "Element",
        },
    )
    vibrato_depth: BezierChainList | None = field(
        default=None,
        metadata={
            "name": "VibratoDepth",
            "type": "Element",
        },
    )
    harmonics: BezierChainList | None = field(
        default=None,
        metadata={
            "name": "Harmonics",
            "type": "Element",
        },
    )
    fx2_depth: BezierChainList | None = field(
        default=None,
        metadata={
            "name": "FX2Depth",
            "type": "Element",
        },
    )
    reso1_freq: BezierChainList | None = field(
        default=None,
        metadata={
            "name": "Reso1Freq",
            "type": "Element",
        },
    )
    reso1_bw: BezierChainList | None = field(
        default=None,
        metadata={
            "name": "Reso1BW",
            "type": "Element",
        },
    )
    reso1_amp: BezierChainList | None = field(
        default=None,
        metadata={
            "name": "Reso1Amp",
            "type": "Element",
        },
    )
    reso2_freq: BezierChainList | None = field(
        default=None,
        metadata={
            "name": "Reso2Freq",
            "type": "Element",
        },
    )
    reso2_bw: BezierChainList | None = field(
        default=None,
        metadata={
            "name": "Reso2BW",
            "type": "Element",
        },
    )
    reso2_amp: BezierChainList | None = field(
        default=None,
        metadata={
            "name": "Reso2Amp",
            "type": "Element",
        },
    )
    reso3_freq: BezierChainList | None = field(
        default=None,
        metadata={
            "name": "Reso3Freq",
            "type": "Element",
        },
    )
    reso3_bw: BezierChainList | None = field(
        default=None,
        metadata={
            "name": "Reso3BW",
            "type": "Element",
        },
    )
    reso3_amp: BezierChainList | None = field(
        default=None,
        metadata={
            "name": "Reso3Amp",
            "type": "Element",
        },
    )
    reso4_freq: BezierChainList | None = field(
        default=None,
        metadata={
            "name": "Reso4Freq",
            "type": "Element",
        },
    )
    reso4_bw: BezierChainList | None = field(
        default=None,
        metadata={
            "name": "Reso4BW",
            "type": "Element",
        },
    )
    reso4_amp: BezierChainList | None = field(
        default=None,
        metadata={
            "name": "Reso4Amp",
            "type": "Element",
        },
    )
    pitch_bend: BezierChainList = field(
        metadata={
            "name": "PitchBend",
            "type": "Element",
            "required": True,
        }
    )
    pitch_bend_sensitivity: BezierChainList = field(
        metadata={
            "name": "PitchBendSensitivity",
            "type": "Element",
            "required": True,
        }
    )


class VsqEvents(BaseModel):
    vsq_event: list[VsqEvent] = field(
        default_factory=list,
        metadata={
            "name": "VsqEvent",
            "type": "Element",
        },
    )


class VsqEventList(BaseModel):
    events: VsqEvents | None = field(
        default=None,
        metadata={
            "name": "Events",
            "type": "Element",
        },
    )


class Curves(BaseModel):
    bezier_curves: list[BezierCurves] = field(
        default_factory=list,
        metadata={
            "name": "BezierCurves",
            "type": "Element",
            "min_occurs": 1,
        },
    )


class VsqMetaText(BaseModel):
    common: VsqCommon = field(
        metadata={
            "name": "Common",
            "type": "Element",
            "required": True,
        }
    )
    events: VsqEventList = field(
        metadata={
            "name": "Events",
            "type": "Element",
            "required": True,
        }
    )
    pit: VsqBPList = field(
        metadata={
            "name": "PIT",
            "type": "Element",
            "required": True,
        }
    )
    pbs: VsqBPList = field(
        metadata={
            "name": "PBS",
            "type": "Element",
            "required": True,
        }
    )
    dyn: VsqBPList = field(
        metadata={
            "name": "DYN",
            "type": "Element",
            "required": True,
        }
    )
    bre: VsqBPList = field(
        metadata={
            "name": "BRE",
            "type": "Element",
            "required": True,
        }
    )
    bri: VsqBPList = field(
        metadata={
            "name": "BRI",
            "type": "Element",
            "required": True,
        }
    )
    cle: VsqBPList = field(
        metadata={
            "name": "CLE",
            "type": "Element",
            "required": True,
        }
    )
    reso1_freq_bplist: VsqBPList = field(
        metadata={
            "name": "reso1FreqBPList",
            "type": "Element",
            "required": True,
        }
    )
    reso2_freq_bplist: VsqBPList = field(
        metadata={
            "name": "reso2FreqBPList",
            "type": "Element",
            "required": True,
        }
    )
    reso3_freq_bplist: VsqBPList = field(
        metadata={
            "name": "reso3FreqBPList",
            "type": "Element",
            "required": True,
        }
    )
    reso4_freq_bplist: VsqBPList = field(
        metadata={
            "name": "reso4FreqBPList",
            "type": "Element",
            "required": True,
        }
    )
    reso1_bwbplist: VsqBPList = field(
        metadata={
            "name": "reso1BWBPList",
            "type": "Element",
            "required": True,
        }
    )
    reso2_bwbplist: VsqBPList = field(
        metadata={
            "name": "reso2BWBPList",
            "type": "Element",
            "required": True,
        }
    )
    reso3_bwbplist: VsqBPList = field(
        metadata={
            "name": "reso3BWBPList",
            "type": "Element",
            "required": True,
        }
    )
    reso4_bwbplist: VsqBPList = field(
        metadata={
            "name": "reso4BWBPList",
            "type": "Element",
            "required": True,
        }
    )
    reso1_amp_bplist: VsqBPList = field(
        metadata={
            "name": "reso1AmpBPList",
            "type": "Element",
            "required": True,
        }
    )
    reso2_amp_bplist: VsqBPList = field(
        metadata={
            "name": "reso2AmpBPList",
            "type": "Element",
            "required": True,
        }
    )
    reso3_amp_bplist: VsqBPList = field(
        metadata={
            "name": "reso3AmpBPList",
            "type": "Element",
            "required": True,
        }
    )
    reso4_amp_bplist: VsqBPList = field(
        metadata={
            "name": "reso4AmpBPList",
            "type": "Element",
            "required": True,
        }
    )
    harmonics: VsqBPList = field(
        metadata={
            "name": "Harmonics",
            "type": "Element",
            "required": True,
        }
    )
    fx2depth: VsqBPList = field(
        metadata={
            "name": "FX2Depth",
            "type": "Element",
            "required": True,
        }
    )
    gen: VsqBPList = field(
        metadata={
            "name": "GEN",
            "type": "Element",
            "required": True,
        }
    )
    por: VsqBPList = field(
        metadata={
            "name": "POR",
            "type": "Element",
            "required": True,
        }
    )
    ope: VsqBPList = field(
        metadata={
            "name": "OPE",
            "type": "Element",
            "required": True,
        }
    )


class AttachedCurves(BaseModel):
    curves: Curves = field(
        metadata={
            "name": "Curves",
            "type": "Element",
            "required": True,
        }
    )


class VsqTrack(BaseModel):
    meta_text: VsqMetaText = field(
        metadata={
            "name": "MetaText",
            "type": "Element",
            "required": True,
        }
    )


class VsqTrackList(BaseModel):
    vsq_track: list[VsqTrack] = field(
        default_factory=list,
        metadata={
            "name": "VsqTrack",
            "type": "Element",
            "min_occurs": 1,
        },
    )


class VsqFileEx(BaseModel):
    track: VsqTrackList = field(
        metadata={
            "name": "Track",
            "type": "Element",
            "required": True,
        }
    )
    tempo_table: TempoTable = field(
        metadata={
            "name": "TempoTable",
            "type": "Element",
            "required": True,
        }
    )
    timesig_table: TimesigTable = field(
        metadata={
            "name": "TimesigTable",
            "type": "Element",
            "required": True,
        }
    )
    total_clocks: int = field(
        metadata={
            "name": "TotalClocks",
            "type": "Element",
            "required": True,
        }
    )
    master: VsqMaster = field(
        metadata={
            "name": "Master",
            "type": "Element",
            "required": True,
        }
    )
    mixer: VsqMixer = field(
        metadata={
            "name": "Mixer",
            "type": "Element",
            "required": True,
        }
    )
    attached_curves: AttachedCurves = field(
        metadata={
            "name": "AttachedCurves",
            "type": "Element",
            "required": True,
        }
    )
    bgm_files: BgmFiles = field(
        metadata={
            "name": "BgmFiles",
            "type": "Element",
            "required": True,
        }
    )
    cache_dir: str = field(
        metadata={
            "name": "cacheDir",
            "type": "Element",
            "required": True,
        }
    )
    config: SequenceConfig = field(
        metadata={
            "type": "Element",
            "required": True,
        }
    )
