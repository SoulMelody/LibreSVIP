import abc
import enum
from functools import partial
from typing import NamedTuple

from pydantic import BaseModel
from xsdata_pydantic.fields import field

from libresvip.utils.binary.midi import (
    DEFAULT_PITCH_BEND_SENSITIVITY,
    MAX_PITCH_BEND_SENSITIVITY,
    PITCH_MAX_VALUE,
    PITCH_MIN_VALUE,
)


class VsqIDType(enum.Enum):
    SINGER = "Singer"
    ANOTE = "Anote"
    AICON = "Aicon"
    UNKNOWN = "Unknown"


class VibratoBPPair(NamedTuple):
    x: float
    y: int


class VibratoBPList(abc.ABC, BaseModel):
    data: str = field(
        default="",
        metadata={
            "name": "Data",
            "type": "Element",
            "required": True,
        },
    )

    def _get_points(self) -> list[VibratoBPPair]:
        pairs = []
        for item in self.data.split(","):
            x, _, y = item.partition("=")
            if x and y:
                pairs.append(VibratoBPPair(float(x), int(y)))
        return pairs

    def _set_points(self, value: list[VibratoBPPair]) -> None:
        self.data = ",".join(f"{x}={y}" for x, y in value)

    points = property(_get_points, _set_points)


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
        default="",
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    feder: int = field(
        default=0,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    panpot: int = field(
        default=0,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    mute: int = field(
        default=0,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    start_after_premeasure: bool = field(
        default=True,
        metadata={
            "name": "startAfterPremeasure",
            "type": "Element",
            "required": True,
        },
    )
    read_offset_seconds: float = field(
        default=0.0,
        metadata={
            "name": "readOffsetSeconds",
            "type": "Element",
            "required": True,
        },
    )


class VsqCommon(BaseModel):
    version: str = field(
        default="",
        metadata={
            "name": "Version",
            "type": "Element",
            "required": True,
        },
    )
    name: str = field(
        default="",
        metadata={
            "name": "Name",
            "type": "Element",
            "required": True,
        },
    )
    color: str = field(
        default="179,181,123",
        metadata={
            "name": "Color",
            "type": "Element",
            "required": True,
        },
    )
    dynamics_mode: int = field(
        default=1,
        metadata={
            "name": "DynamicsMode",
            "type": "Element",
            "required": True,
        },
    )
    play_mode: int = field(
        default=1,
        metadata={
            "name": "PlayMode",
            "type": "Element",
            "required": True,
        },
    )
    last_play_mode: int = field(
        default=1,
        metadata={
            "name": "LastPlayMode",
            "type": "Element",
            "required": True,
        },
    )


class IconHandle(BaseModel):
    caption: str = field(
        default="",
        metadata={
            "name": "Caption",
            "type": "Element",
            "required": True,
        },
    )
    icon_id: str = field(
        default="",
        metadata={
            "name": "IconID",
            "type": "Element",
            "required": True,
        },
    )
    ids: str = field(
        default="",
        metadata={
            "name": "IDS",
            "type": "Element",
            "required": True,
        },
    )
    index: int = field(
        default=0,
        metadata={
            "name": "Index",
            "type": "Element",
            "required": True,
        },
    )
    length: int = field(
        default=1,
        metadata={
            "name": "Length",
            "type": "Element",
            "required": True,
        },
    )
    original: int = field(
        default=0,
        metadata={
            "name": "Original",
            "type": "Element",
            "required": True,
        },
    )
    program: int = field(
        default=0,
        metadata={
            "name": "Program",
            "type": "Element",
            "required": True,
        },
    )
    language: int = field(
        default=0,
        metadata={
            "name": "Language",
            "type": "Element",
            "required": True,
        },
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
        default=1,
        metadata={
            "name": "UnknownFloat",
            "type": "Element",
        },
    )
    phonetic_symbol_protected: bool | None = field(
        default=False,
        metadata={
            "name": "PhoneticSymbolProtected",
            "type": "Element",
        },
    )
    consonant_adjustment: int | str | None = field(
        default=0,
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
        default=1,
        metadata={
            "name": "PreMeasure",
            "type": "Element",
            "required": True,
        },
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
        default=0,
        metadata={
            "name": "Index",
            "type": "Element",
            "required": True,
        },
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
        default=-1,
        metadata={
            "name": "Note",
            "type": "Element",
            "required": True,
        },
    )
    intensity: int = field(
        default=100,
        metadata={
            "name": "Intensity",
            "type": "Element",
            "required": True,
        },
    )
    pbtype: int = field(
        default=-1,
        metadata={
            "name": "PBType",
            "type": "Element",
            "required": True,
        },
    )
    tempo: int = field(
        default=-1,
        metadata={
            "name": "Tempo",
            "type": "Element",
            "required": True,
        },
    )
    pre_utterance: int = field(
        default=0,
        metadata={
            "name": "PreUtterance",
            "type": "Element",
            "required": True,
        },
    )
    voice_overlap: int = field(
        default=0,
        metadata={
            "name": "VoiceOverlap",
            "type": "Element",
            "required": True,
        },
    )
    moduration: int = field(
        default=100,
        metadata={
            "name": "Moduration",
            "type": "Element",
            "required": True,
        },
    )
    start_point: int = field(
        default=0,
        metadata={
            "name": "StartPoint",
            "type": "Element",
            "required": True,
        },
    )
    length: int = field(
        default=0,
        metadata={
            "name": "Length",
            "type": "Element",
            "required": True,
        },
    )


class VsqMixerEntry(BaseModel):
    feder: int = field(
        default=0,
        metadata={
            "name": "Feder",
            "type": "Element",
            "required": True,
        },
    )
    panpot: int = field(
        default=0,
        metadata={
            "name": "Panpot",
            "type": "Element",
            "required": True,
        },
    )
    mute: int = field(
        default=0,
        metadata={
            "name": "Mute",
            "type": "Element",
            "required": True,
        },
    )
    solo: int = field(
        default=0,
        metadata={
            "name": "Solo",
            "type": "Element",
            "required": True,
        },
    )


class SequenceConfig(BaseModel):
    class Meta:
        name = "config"

    sampling_rate: int = field(
        default=44100,
        metadata={
            "name": "SamplingRate",
            "type": "Element",
            "required": True,
        },
    )
    wave_file_output_channel: int = field(
        default=2,
        metadata={
            "name": "WaveFileOutputChannel",
            "type": "Element",
            "required": True,
        },
    )
    wave_file_output_from_master_track: bool = field(
        default=False,
        metadata={
            "name": "WaveFileOutputFromMasterTrack",
            "type": "Element",
            "required": True,
        },
    )
    start_marker: int = field(
        default=0,
        metadata={
            "name": "StartMarker",
            "type": "Element",
            "required": True,
        },
    )
    start_marker_enabled: bool = field(
        default=False,
        metadata={
            "name": "StartMarkerEnabled",
            "type": "Element",
            "required": True,
        },
    )
    end_marker: int = field(
        default=0,
        metadata={
            "name": "EndMarker",
            "type": "Element",
            "required": True,
        },
    )
    end_marker_enabled: bool = field(
        default=False,
        metadata={
            "name": "EndMarkerEnabled",
            "type": "Element",
            "required": True,
        },
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
    bgm_file: list[BgmFile] = field(
        default_factory=list,
        metadata={
            "name": "BgmFile",
            "type": "Element",
        },
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
        },
    )


class TempoTable(BaseModel):
    tempo_table_entry: list[TempoTableEntry] = field(
        default_factory=list,
        metadata={
            "name": "TempoTableEntry",
            "type": "Element",
        },
    )


class TimesigTable(BaseModel):
    time_sig_table_entry: list[TimeSigTableEntry] = field(
        default_factory=list,
        metadata={
            "name": "TimeSigTableEntry",
            "type": "Element",
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
        default=0,
        metadata={
            "name": "Index",
            "type": "Element",
            "required": True,
        },
    )
    trailing: Trailing = field(
        default_factory=Trailing,
        metadata={
            "name": "Trailing",
            "type": "Element",
            "required": True,
        },
    )


class VsqMixer(BaseModel):
    master_feder: int = field(
        default=0,
        metadata={
            "name": "MasterFeder",
            "type": "Element",
            "required": True,
        },
    )
    master_panpot: int = field(
        default=0,
        metadata={
            "name": "MasterPanpot",
            "type": "Element",
            "required": True,
        },
    )
    master_mute: int = field(
        default=0,
        metadata={
            "name": "MasterMute",
            "type": "Element",
            "required": True,
        },
    )
    output_mode: int = field(
        default=0,
        metadata={
            "name": "OutputMode",
            "type": "Element",
            "required": True,
        },
    )
    slave: Slave = field(
        default_factory=Slave,
        metadata={
            "name": "Slave",
            "type": "Element",
            "required": True,
        },
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

    type_value: VsqIDType = field(
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
        default=64,
        metadata={
            "name": "Dynamics",
            "type": "Element",
            "required": True,
        },
    )
    pmbend_depth: int = field(
        default=8,
        metadata={
            "name": "PMBendDepth",
            "type": "Element",
            "required": True,
        },
    )
    pmbend_length: int = field(
        default=0,
        metadata={
            "name": "PMBendLength",
            "type": "Element",
            "required": True,
        },
    )
    pmb_portamento_use: int = field(
        default=3,
        metadata={
            "name": "PMbPortamentoUse",
            "type": "Element",
            "required": True,
        },
    )
    demdec_gain_rate: int = field(
        default=50,
        metadata={
            "name": "DEMdecGainRate",
            "type": "Element",
            "required": True,
        },
    )
    demaccent: int = field(
        default=50,
        metadata={
            "name": "DEMaccent",
            "type": "Element",
            "required": True,
        },
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
        default=0,
        metadata={
            "name": "VibratoDelay",
            "type": "Element",
            "required": True,
        },
    )
    note_head_handle: NoteHeadHandle | None = field(
        default=None,
        metadata={
            "name": "NoteHeadHandle",
            "type": "Element",
        },
    )
    p_mean_onset_first_note: int = field(
        default=10,
        metadata={
            "name": "pMeanOnsetFirstNote",
            "type": "Element",
            "required": True,
        },
    )
    v_mean_note_transition: int = field(
        default=12,
        metadata={
            "name": "vMeanNoteTransition",
            "type": "Element",
            "required": True,
        },
    )
    d4mean: int = field(
        default=24,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    p_mean_ending_note: int = field(
        default=12,
        metadata={
            "name": "pMeanEndingNote",
            "type": "Element",
            "required": True,
        },
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
        default_factory=UstEvent,
        metadata={
            "name": "UstEvent",
            "type": "Element",
            "required": True,
        },
    )


class BezierCurves(BaseModel):
    dynamics: BezierChainList = field(
        default_factory=BezierChainList,
        metadata={
            "name": "Dynamics",
            "type": "Element",
            "required": True,
        },
    )
    brethiness: BezierChainList = field(
        default_factory=BezierChainList,
        metadata={
            "name": "Brethiness",
            "type": "Element",
            "required": True,
        },
    )
    brightness: BezierChainList = field(
        default_factory=BezierChainList,
        metadata={
            "name": "Brightness",
            "type": "Element",
            "required": True,
        },
    )
    clearness: BezierChainList = field(
        default_factory=BezierChainList,
        metadata={
            "name": "Clearness",
            "type": "Element",
            "required": True,
        },
    )
    opening: BezierChainList = field(
        default_factory=BezierChainList,
        metadata={
            "name": "Opening",
            "type": "Element",
            "required": True,
        },
    )
    gender_factor: BezierChainList = field(
        default_factory=BezierChainList,
        metadata={
            "name": "GenderFactor",
            "type": "Element",
            "required": True,
        },
    )
    portamento_timing: BezierChainList = field(
        default_factory=BezierChainList,
        metadata={
            "name": "PortamentoTiming",
            "type": "Element",
            "required": True,
        },
    )
    vibrato_rate: BezierChainList | None = field(
        default_factory=BezierChainList,
        metadata={
            "name": "VibratoRate",
            "type": "Element",
        },
    )
    vibrato_depth: BezierChainList | None = field(
        default_factory=BezierChainList,
        metadata={
            "name": "VibratoDepth",
            "type": "Element",
        },
    )
    harmonics: BezierChainList | None = field(
        default_factory=BezierChainList,
        metadata={
            "name": "Harmonics",
            "type": "Element",
        },
    )
    fx2_depth: BezierChainList | None = field(
        default_factory=BezierChainList,
        metadata={
            "name": "FX2Depth",
            "type": "Element",
        },
    )
    reso1_freq: BezierChainList | None = field(
        default_factory=BezierChainList,
        metadata={
            "name": "Reso1Freq",
            "type": "Element",
        },
    )
    reso1_bw: BezierChainList | None = field(
        default_factory=BezierChainList,
        metadata={
            "name": "Reso1BW",
            "type": "Element",
        },
    )
    reso1_amp: BezierChainList | None = field(
        default_factory=BezierChainList,
        metadata={
            "name": "Reso1Amp",
            "type": "Element",
        },
    )
    reso2_freq: BezierChainList | None = field(
        default_factory=BezierChainList,
        metadata={
            "name": "Reso2Freq",
            "type": "Element",
        },
    )
    reso2_bw: BezierChainList | None = field(
        default_factory=BezierChainList,
        metadata={
            "name": "Reso2BW",
            "type": "Element",
        },
    )
    reso2_amp: BezierChainList | None = field(
        default_factory=BezierChainList,
        metadata={
            "name": "Reso2Amp",
            "type": "Element",
        },
    )
    reso3_freq: BezierChainList | None = field(
        default_factory=BezierChainList,
        metadata={
            "name": "Reso3Freq",
            "type": "Element",
        },
    )
    reso3_bw: BezierChainList | None = field(
        default_factory=BezierChainList,
        metadata={
            "name": "Reso3BW",
            "type": "Element",
        },
    )
    reso3_amp: BezierChainList | None = field(
        default_factory=BezierChainList,
        metadata={
            "name": "Reso3Amp",
            "type": "Element",
        },
    )
    reso4_freq: BezierChainList | None = field(
        default_factory=BezierChainList,
        metadata={
            "name": "Reso4Freq",
            "type": "Element",
        },
    )
    reso4_bw: BezierChainList | None = field(
        default_factory=BezierChainList,
        metadata={
            "name": "Reso4BW",
            "type": "Element",
        },
    )
    reso4_amp: BezierChainList | None = field(
        default_factory=BezierChainList,
        metadata={
            "name": "Reso4Amp",
            "type": "Element",
        },
    )
    pitch_bend: BezierChainList = field(
        default_factory=BezierChainList,
        metadata={
            "name": "PitchBend",
            "type": "Element",
            "required": True,
        },
    )
    pitch_bend_sensitivity: BezierChainList = field(
        default_factory=BezierChainList,
        metadata={
            "name": "PitchBendSensitivity",
            "type": "Element",
            "required": True,
        },
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
        },
    )


class VsqMetaText(BaseModel):
    common: VsqCommon = field(
        default_factory=VsqCommon,
        metadata={
            "name": "Common",
            "type": "Element",
            "required": True,
        },
    )
    events: VsqEventList = field(
        default_factory=VsqEventList,
        metadata={
            "name": "Events",
            "type": "Element",
            "required": True,
        },
    )
    pit: VsqBPList = field(
        default_factory=partial(
            VsqBPList, default=0, name="pit", maximum=PITCH_MAX_VALUE, minimum=PITCH_MIN_VALUE
        ),
        metadata={
            "name": "PIT",
            "type": "Element",
            "required": True,
        },
    )
    pbs: VsqBPList = field(
        default_factory=partial(
            VsqBPList,
            default=DEFAULT_PITCH_BEND_SENSITIVITY,
            name="pbs",
            maximum=MAX_PITCH_BEND_SENSITIVITY,
            minimum=0,
        ),
        metadata={
            "name": "PBS",
            "type": "Element",
            "required": True,
        },
    )
    dyn: VsqBPList = field(
        default_factory=partial(VsqBPList, default=64, name="dyn", maximum=127, minimum=0),
        metadata={
            "name": "DYN",
            "type": "Element",
            "required": True,
        },
    )
    bre: VsqBPList = field(
        default_factory=partial(VsqBPList, default=0, name="bre", maximum=127, minimum=0),
        metadata={
            "name": "BRE",
            "type": "Element",
            "required": True,
        },
    )
    bri: VsqBPList = field(
        default_factory=partial(VsqBPList, default=0, name="bri", maximum=127, minimum=0),
        metadata={
            "name": "BRI",
            "type": "Element",
            "required": True,
        },
    )
    cle: VsqBPList = field(
        default_factory=partial(VsqBPList, default=0, name="cle", maximum=127, minimum=0),
        metadata={
            "name": "CLE",
            "type": "Element",
            "required": True,
        },
    )
    reso1_freq_bplist: VsqBPList = field(
        default_factory=partial(VsqBPList, default=64, name="reso1freq", maximum=127, minimum=0),
        metadata={
            "name": "reso1FreqBPList",
            "type": "Element",
            "required": True,
        },
    )
    reso2_freq_bplist: VsqBPList = field(
        default_factory=partial(VsqBPList, default=64, name="reso2freq", maximum=127, minimum=0),
        metadata={
            "name": "reso2FreqBPList",
            "type": "Element",
            "required": True,
        },
    )
    reso3_freq_bplist: VsqBPList = field(
        default_factory=partial(VsqBPList, default=64, name="reso3freq", maximum=127, minimum=0),
        metadata={
            "name": "reso3FreqBPList",
            "type": "Element",
            "required": True,
        },
    )
    reso4_freq_bplist: VsqBPList = field(
        default_factory=partial(VsqBPList, default=64, name="reso4freq", maximum=127, minimum=0),
        metadata={
            "name": "reso4FreqBPList",
            "type": "Element",
            "required": True,
        },
    )
    reso1_bwbplist: VsqBPList = field(
        default_factory=partial(VsqBPList, default=64, name="reso1bw", maximum=127, minimum=0),
        metadata={
            "name": "reso1BWBPList",
            "type": "Element",
            "required": True,
        },
    )
    reso2_bwbplist: VsqBPList = field(
        default_factory=partial(VsqBPList, default=64, name="reso2bw", maximum=127, minimum=0),
        metadata={
            "name": "reso2BWBPList",
            "type": "Element",
            "required": True,
        },
    )
    reso3_bwbplist: VsqBPList = field(
        default_factory=partial(VsqBPList, default=64, name="reso3bw", maximum=127, minimum=0),
        metadata={
            "name": "reso3BWBPList",
            "type": "Element",
            "required": True,
        },
    )
    reso4_bwbplist: VsqBPList = field(
        default_factory=partial(VsqBPList, default=64, name="reso4bw", maximum=127, minimum=0),
        metadata={
            "name": "reso4BWBPList",
            "type": "Element",
            "required": True,
        },
    )
    reso1_amp_bplist: VsqBPList = field(
        default_factory=partial(VsqBPList, default=64, name="reso1amp", maximum=127, minimum=0),
        metadata={
            "name": "reso1AmpBPList",
            "type": "Element",
            "required": True,
        },
    )
    reso2_amp_bplist: VsqBPList = field(
        default_factory=partial(VsqBPList, default=64, name="reso2amp", maximum=127, minimum=0),
        metadata={
            "name": "reso2AmpBPList",
            "type": "Element",
            "required": True,
        },
    )
    reso3_amp_bplist: VsqBPList = field(
        default_factory=partial(VsqBPList, default=64, name="reso3amp", maximum=127, minimum=0),
        metadata={
            "name": "reso3AmpBPList",
            "type": "Element",
            "required": True,
        },
    )
    reso4_amp_bplist: VsqBPList = field(
        default_factory=partial(VsqBPList, default=64, name="reso4amp", maximum=127, minimum=0),
        metadata={
            "name": "reso4AmpBPList",
            "type": "Element",
            "required": True,
        },
    )
    harmonics: VsqBPList = field(
        default_factory=partial(VsqBPList, default=64, name="harmonics", maximum=127, minimum=0),
        metadata={
            "name": "harmonics",
            "type": "Element",
            "required": True,
        },
    )
    fx2depth: VsqBPList = field(
        default_factory=partial(VsqBPList, default=64, name="fx2depth", maximum=127, minimum=0),
        metadata={
            "name": "fx2depth",
            "type": "Element",
            "required": True,
        },
    )
    gen: VsqBPList = field(
        default_factory=partial(VsqBPList, default=64, name="gen", maximum=127, minimum=0),
        metadata={
            "name": "GEN",
            "type": "Element",
            "required": True,
        },
    )
    por: VsqBPList = field(
        default_factory=partial(VsqBPList, default=64, name="por", maximum=127, minimum=0),
        metadata={
            "name": "POR",
            "type": "Element",
            "required": True,
        },
    )
    ope: VsqBPList = field(
        default_factory=partial(VsqBPList, default=127, name="ope", maximum=127, minimum=0),
        metadata={
            "name": "OPE",
            "type": "Element",
            "required": True,
        },
    )


class AttachedCurves(BaseModel):
    curves: Curves = field(
        default_factory=Curves,
        metadata={
            "name": "Curves",
            "type": "Element",
            "required": True,
        },
    )


class VsqTrack(BaseModel):
    meta_text: VsqMetaText | None = field(
        default=None,
        metadata={
            "name": "MetaText",
            "type": "Element",
        },
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
        default_factory=VsqTrackList,
        metadata={
            "name": "Track",
            "type": "Element",
            "required": True,
        },
    )
    tempo_table: TempoTable = field(
        default_factory=TempoTable,
        metadata={
            "name": "TempoTable",
            "type": "Element",
            "required": True,
        },
    )
    timesig_table: TimesigTable = field(
        default_factory=TimesigTable,
        metadata={
            "name": "TimesigTable",
            "type": "Element",
            "required": True,
        },
    )
    total_clocks: int = field(
        default=0,
        metadata={
            "name": "TotalClocks",
            "type": "Element",
            "required": True,
        },
    )
    master: VsqMaster = field(
        default_factory=VsqMaster,
        metadata={
            "name": "Master",
            "type": "Element",
            "required": True,
        },
    )
    mixer: VsqMixer = field(
        default_factory=VsqMixer,
        metadata={
            "name": "Mixer",
            "type": "Element",
            "required": True,
        },
    )
    attached_curves: AttachedCurves = field(
        default_factory=AttachedCurves,
        metadata={
            "name": "AttachedCurves",
            "type": "Element",
            "required": True,
        },
    )
    bgm_files: BgmFiles = field(
        default_factory=BgmFiles,
        metadata={
            "name": "BgmFiles",
            "type": "Element",
            "required": True,
        },
    )
    cache_dir: str = field(
        default="",
        metadata={
            "name": "cacheDir",
            "type": "Element",
            "required": True,
        },
    )
    config: SequenceConfig = field(
        default_factory=SequenceConfig,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
