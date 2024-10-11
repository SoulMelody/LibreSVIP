# Ported from QSvip by SineStriker
import abc
import dataclasses
import enum
import inspect
import math
import struct
from itertools import chain
from typing import Generic, Literal, NamedTuple, Optional, TypeVar

from more_itertools import batched

XSItem = TypeVar("XSItem")
MIN_NOTE_DURATION = 0.045
MAX_NOTE_DURATION = 20.0


def to_backing_field(key: str) -> str:
    return f"<{key}>k__BackingField"


class XSLineParamNode(NamedTuple):
    pos: int = 0
    value: int = 0


@dataclasses.dataclass
class XSLineParam:
    """SingingTool.Model.Line.LineParam"""

    line_param: bytes = dataclasses.field(
        default=b"",
        metadata={
            "alias": "LineParam",
        },
    )
    nodes: list[XSLineParamNode] = dataclasses.field(init=False)

    def __post_init__(self) -> None:
        self.nodes = []
        if len(self.line_param) >= 4:
            (node_count,) = struct.unpack("<i", bytearray(self.line_param[:4]))
            self.nodes.extend(
                XSLineParamNode._make(each)
                for each in batched(
                    struct.unpack(
                        f"<{node_count * 2}i",
                        bytearray(self.line_param[4 : 4 + node_count * 8]),
                    ),
                    2,
                )
            )

    def convert_to_param(self) -> None:
        self.line_param = struct.pack("<i", len(self.nodes))
        self.line_param += struct.pack(f"<{len(self.nodes) * 2}i", *chain.from_iterable(self.nodes))
        expected_len = max(64, 2 ** math.ceil(math.log2(len(self.line_param))))
        if len(self.line_param) < expected_len:
            self.line_param += b"\x00" * (expected_len - len(self.line_param))


@dataclasses.dataclass
class XSVibratoStyle:
    """SingingTool.Model.VibratoStyle"""

    amp_line: XSLineParam = dataclasses.field(
        default_factory=XSLineParam,
        metadata={"alias": "_ampLine", "order": 0},
    )
    freq_line: XSLineParam = dataclasses.field(
        default_factory=XSLineParam,
        metadata={"alias": "_freqLine", "order": 1},
    )
    is_anti_phase: bool = dataclasses.field(
        default=False,
        metadata={
            "alias": to_backing_field("IsAntiPhase"),
        },
    )


@dataclasses.dataclass
class XSVibratoPercentInfo:
    """SingingTool.Model.VibratoPercentInfo"""

    start_percent: float = dataclasses.field(
        default=0,
        metadata={"alias": "_startPercent", "order": 0},
    )
    end_percent: float = dataclasses.field(
        default=100,
        metadata={"alias": "_endPercent", "order": 1},
    )


class XSReverbPresetEnum(enum.IntEnum):
    NONE = -1
    DEFAULT = enum.auto()
    SMALLHALL1 = enum.auto()
    SMALLHALL2 = enum.auto()
    MEDIUMHALL1 = enum.auto()
    MEDIUMHALL2 = enum.auto()
    LARGEHALL1 = enum.auto()
    LARGEHALL2 = enum.auto()
    SMALLROOM1 = enum.auto()
    SMALLROOM2 = enum.auto()
    MEDIUMROOM1 = enum.auto()
    MEDIUMROOM2 = enum.auto()
    LARGEROOM1 = enum.auto()
    LARGEROOM2 = enum.auto()
    MEDIUMER1 = enum.auto()
    MEDIUMER2 = enum.auto()
    PLATEHIGH = enum.auto()
    PLATELOW = enum.auto()
    LONGREVERB1 = enum.auto()
    LONGREVERB2 = enum.auto()


@dataclasses.dataclass
class XSReverbPreset:
    """SingingTool.Library.Audio.ReverbPreset"""

    value: XSReverbPresetEnum = dataclasses.field(
        default=XSReverbPresetEnum.NONE,
        metadata={
            "alias": "value__",
        },
    )


@dataclasses.dataclass
class XSIOverlappable:
    overlapped: bool = dataclasses.field(
        default=False,
        metadata={"alias": to_backing_field("Overlaped"), "order": 6},
    )


@dataclasses.dataclass
class XSBeatSize:
    """SingingTool.Model.SingingGeneralConcept.BeatSize"""

    x: int = dataclasses.field(
        default=0,
        metadata={"alias": "_x", "order": 0},
    )
    y: int = dataclasses.field(
        default=0,
        metadata={"alias": "_y", "order": 1},
    )


@dataclasses.dataclass
class XSSongBeat(XSIOverlappable):
    """SingingTool.Model.SingingGeneralConcept.SongBeat"""

    bar_index: int = dataclasses.field(
        default=0,
        metadata={
            "alias": "_barIndex",
            "order": 0,
        },
    )
    beat_size: XSBeatSize = dataclasses.field(
        default_factory=XSBeatSize,
        metadata={
            "alias": "_beatSize",
            "order": 1,
        },
    )


@dataclasses.dataclass
class XSSongTempo(XSIOverlappable):
    """SingingTool.Model.SingingGeneralConcept.SongTempo"""

    pos: int = dataclasses.field(
        default=0,
        metadata={
            "alias": "_pos",
            "order": 0,
        },
    )
    tempo: int = dataclasses.field(
        default=120,
        metadata={
            "alias": "_tempo",
            "order": 1,
        },
    )


class XSNoteHeadTagEnum(enum.IntEnum):
    NoTag = 0
    SilTag = 1
    SpTag = 2


@dataclasses.dataclass
class XSNoteHeadTag:
    """SingingTool.Model.NoteHeadTag"""

    value: XSNoteHeadTagEnum = dataclasses.field(
        default=XSNoteHeadTagEnum.NoTag,
        metadata={
            "alias": "value__",
        },
    )


@dataclasses.dataclass
class XSNotePhoneInfo:
    """SingingTool.Model.NotePhoneInfo"""

    head_phone_time_in_sec: float = dataclasses.field(
        default=0,
        metadata={
            "alias": to_backing_field("HeadPhoneTimeInSec"),
            "order": 0,
        },
    )
    mid_part_over_tail_part_ratio: float = dataclasses.field(
        default=0,
        metadata={
            "alias": to_backing_field("MidPartOverTailPartRatio"),
            "order": 1,
        },
    )


@dataclasses.dataclass
class XSNote(XSIOverlappable):
    """SingingTool.Model.Note"""

    start_pos: int = dataclasses.field(
        default=0,
        metadata={"alias": "_startPos", "order": 0},
    )
    width_pos: int = dataclasses.field(
        default=480,
        metadata={"alias": "_widthPos", "order": 1},
    )
    key_index: int = dataclasses.field(
        default=60,
        metadata={"alias": "_keyIndex", "order": 2},
    )
    lyric: str = dataclasses.field(
        default="",
        metadata={"alias": "_lyric", "order": 3},
    )
    pronouncing: str = dataclasses.field(
        default="",
        metadata={"alias": "_pronouncing", "order": 4},
    )
    head_tag: XSNoteHeadTag = dataclasses.field(
        default_factory=XSNoteHeadTag,
        metadata={"alias": "_headTag", "order": 5},
    )
    note_phone_info: Optional[XSNotePhoneInfo] = dataclasses.field(
        default=None,
        metadata={"alias": to_backing_field("NotePhoneInfo"), "order": 7},
    )
    vibrato_percent: int = dataclasses.field(
        default=0,
        metadata={"alias": to_backing_field("VibratoPercent"), "order": 8},
    )
    vibrato: Optional[XSVibratoStyle] = dataclasses.field(
        default=None,
        metadata={"alias": to_backing_field("Vibrato"), "order": 9},
    )
    vibrato_percent_info: Optional[XSVibratoPercentInfo] = dataclasses.field(
        default=None,
        metadata={
            "alias": to_backing_field("VibratoPercentInfo"),
            "order": 10,
        },
    )


@dataclasses.dataclass
class XSBuf(Generic[XSItem]):
    """System.Collections.Generic.List"""

    items: list[XSItem] = dataclasses.field(
        default_factory=list,
        metadata={
            "alias": "_items",
            "order": 0,
        },
    )
    size: int = dataclasses.field(
        default=0,
        metadata={
            "alias": "_size",
            "order": 1,
        },
    )
    version: int = dataclasses.field(
        default=0,
        metadata={
            "alias": "_version",
            "order": 2,
        },
    )


@dataclasses.dataclass
class XSBufList(Generic[XSItem]):
    """SingingTool.Library.SerialOverlapableItemList"""

    buf: XSBuf[XSItem] = dataclasses.field(
        default_factory=XSBuf[XSItem],
        metadata={
            "alias": "_buf",
            "order": 0,
        },
    )
    buf_1: XSBuf[XSItem] = dataclasses.field(
        default_factory=XSBuf[XSItem],
        metadata={
            "alias": "SerialItemList`1+_buf",
            "order": 1,
        },
    )


class XSTrackType(enum.Enum):
    Singing = enum.auto()
    Instrument = enum.auto()


@dataclasses.dataclass
class XSITrack(abc.ABC):
    """SingingTool.Model.ITrack"""

    track_type: XSTrackType
    pan: float = dataclasses.field(
        default=0,
        metadata={
            "alias": "_pan",
            "order": 9,
        },
    )
    name: str = dataclasses.field(
        default="",
        metadata={
            "alias": "_name",
            "order": 10,
        },
    )
    mute: bool = dataclasses.field(
        default=False,
        metadata={
            "alias": "_mute",
            "order": 11,
        },
    )
    solo: bool = dataclasses.field(
        default=False,
        metadata={
            "alias": "_solo",
            "order": 12,
        },
    )
    volume: float = dataclasses.field(
        default=0.7,
        metadata={
            "alias": "_volume",
            "order": 8,
        },
    )


@dataclasses.dataclass
class XSSingingTrack(XSITrack):
    """SingingTool.Model.SingingTrack"""

    track_type: Literal[XSTrackType.Singing] = XSTrackType.Singing
    note_list: XSBufList[XSNote] = dataclasses.field(
        default_factory=XSBufList[XSNote],
        metadata={
            "alias": "_noteList",
            "order": 0,
        },
    )
    need_refresh_base_metadata_flag: bool = dataclasses.field(
        default=False,
        metadata={
            "alias": "_needRefreshBaseMetadataFlag",
            "order": 1,
        },
    )
    edited_pitch_line: XSLineParam = dataclasses.field(
        default_factory=XSLineParam,
        metadata={
            "alias": "_editedPitchLine",
            "order": 2,
        },
    )
    edited_volume_line: XSLineParam = dataclasses.field(
        default_factory=XSLineParam,
        metadata={
            "alias": "_editedVolumeLine",
            "order": 3,
        },
    )
    edited_breath_line: XSLineParam = dataclasses.field(
        default_factory=XSLineParam,
        metadata={
            "alias": "_editedBreathLine",
            "order": 4,
        },
    )
    edited_gender_line: XSLineParam = dataclasses.field(
        default_factory=XSLineParam,
        metadata={
            "alias": "_editedGenderLine",
            "order": 5,
        },
    )
    edited_power_line: Optional[XSLineParam] = dataclasses.field(
        default=None,
        metadata={
            "alias": "_editedPowerLine",
            "order": 6,
        },
    )
    reverb_preset: XSReverbPreset = dataclasses.field(
        default_factory=XSReverbPreset,
        metadata={
            "alias": "_reverbPreset",
            "order": 7,
        },
    )
    ai_singer_id: str = dataclasses.field(
        default="",
        metadata={
            "alias": to_backing_field("AISingerId"),
            "order": 13,
        },
    )


@dataclasses.dataclass
class XSInstrumentTrack(XSITrack):
    """SingingTool.Model.InstrumentTrack"""

    track_type: Literal[XSTrackType.Instrument] = XSTrackType.Instrument
    volume: float = dataclasses.field(
        default=0.3,
        metadata={
            "alias": "_volume",
            "order": 8,
        },
    )
    sample_rate: float = dataclasses.field(
        default=48000,
        metadata={
            "alias": to_backing_field("SampleRate"),
            "order": 14,
        },
    )
    sample_count: int = dataclasses.field(
        default=0,
        metadata={
            "alias": to_backing_field("SampleCount"),
            "order": 15,
        },
    )
    channel_count: int = dataclasses.field(
        default=0,
        metadata={
            "alias": to_backing_field("ChannelCount"),
            "order": 16,
        },
    )
    offset_in_pos: int = dataclasses.field(
        default=0,
        metadata={
            "alias": to_backing_field("OffsetInPos"),
            "order": 17,
        },
    )
    instrument_file_path: str = dataclasses.field(
        default="",
        metadata={
            "alias": to_backing_field("InstrumentFilePath"),
            "order": 18,
        },
    )


@dataclasses.dataclass
class XSAppModel:
    """SingingTool.Model.AppModel"""

    project_file_path: str = dataclasses.field(
        default="",
        metadata={
            "alias": to_backing_field("ProjectFilePath"),
            "order": 0,
        },
    )
    tempo_list: XSBufList[XSSongTempo] = dataclasses.field(
        default_factory=XSBufList[XSSongTempo],
        metadata={
            "alias": "_tempoList",
            "order": 1,
        },
    )
    beat_list: XSBufList[XSSongBeat] = dataclasses.field(
        default_factory=XSBufList[XSSongBeat],
        metadata={
            "alias": "_beatList",
            "order": 2,
        },
    )
    track_list: XSBuf[XSITrack] = dataclasses.field(
        default_factory=XSBuf[XSITrack],
        metadata={
            "alias": "_trackList",
            "order": 3,
        },
    )
    quantize: int = dataclasses.field(
        default=8,
        metadata={
            "alias": "_quantize",
            "order": 4,
        },
    )
    is_triplet: bool = dataclasses.field(
        default=False,
        metadata={
            "alias": "_isTriplet",
            "order": 5,
        },
    )
    is_numerical_key_name: bool = dataclasses.field(
        default=True,
        metadata={
            "alias": "_isNumerialKeyName",
            "order": 6,
        },
    )
    first_numerical_key_name_at_index: int = dataclasses.field(
        default=0,
        metadata={
            "alias": "_firstNumerialKeyNameAtIndex",
            "order": 7,
        },
    )
    actual_project_file_path: Optional[str] = dataclasses.field(
        default=None,
        metadata={
            "alias": to_backing_field("ActualProjectFilePath"),
            "order": 8,
        },
    )


fullname2classes = {
    inspect.getdoc(cls): cls
    for cls in (
        XSAppModel,
        XSBeatSize,
        XSSongBeat,
        XSITrack,
        XSLineParam,
        XSBufList,
        XSSongTempo,
        XSITrack,
        XSBuf,
        XSSingingTrack,
        XSInstrumentTrack,
        XSVibratoPercentInfo,
        XSVibratoStyle,
        XSNotePhoneInfo,
        XSNoteHeadTag,
        XSNote,
        XSReverbPreset,
    )
}
