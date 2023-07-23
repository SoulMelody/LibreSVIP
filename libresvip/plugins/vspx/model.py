import abc
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class VSPXParamBase(abc.ABC):
    time: Optional[int] = field(
        default=None,
        metadata={
            "name": "t",
            "type": "Element",
        },
    )
    value: Optional[int] = field(
        default=None,
        metadata={
            "name": "v",
            "type": "Element",
        },
    )


@dataclass
class BRE(VSPXParamBase):
    class Meta:
        name = "B"


@dataclass
class DYN(VSPXParamBase):
    class Meta:
        name = "D"


@dataclass
class GEN(VSPXParamBase):
    class Meta:
        name = "G"


@dataclass
class PIT(VSPXParamBase):
    class Meta:
        name = "P"


@dataclass
class BRI(VSPXParamBase):
    class Meta:
        name = "R"


@dataclass
class STR(VSPXParamBase):
    class Meta:
        name = "S"


@dataclass
class VOC(VSPXParamBase):
    class Meta:
        name = "V"


@dataclass
class GWL(VSPXParamBase):
    class Meta:
        name = "W"


@dataclass
class XSY(VSPXParamBase):
    class Meta:
        name = "X"


@dataclass
class Beat:
    bar_index: Optional[int] = field(
        default=0,
        metadata={
            "name": "barIndex",
            "type": "Element",
        },
    )
    beat_per_bar: Optional[int] = field(
        default=4,
        metadata={
            "name": "beatPerBar",
            "type": "Element",
        },
    )
    bar_divide: Optional[int] = field(
        default=4,
        metadata={
            "name": "barDivide",
            "type": "Element",
        },
    )


@dataclass
class DefaultParameter:
    dyn: Optional[int] = field(
        default=128,
        metadata={
            "type": "Element",
        },
    )
    strength: Optional[int] = field(
        default=128,
        metadata={
            "name": "str",
            "type": "Element",
        },
    )
    bri: Optional[int] = field(
        default=128,
        metadata={
            "type": "Element",
        },
    )
    voc: Optional[int] = field(
        default=255,
        metadata={
            "type": "Element",
        },
    )
    bre: Optional[int] = field(
        default=128,
        metadata={
            "type": "Element",
        },
    )
    gen: Optional[int] = field(
        default=128,
        metadata={
            "type": "Element",
        },
    )
    gwl: Optional[int] = field(
        default=0,
        metadata={
            "type": "Element",
        },
    )
    xsy: Optional[int] = field(
        default=0,
        metadata={
            "type": "Element",
        },
    )


@dataclass
class Trill:
    pos: Optional[float] = field(
        default=0.25,
        metadata={
            "type": "Element",
        },
    )
    amplitude: Optional[float] = field(
        default=0.5,
        metadata={
            "type": "Element",
        },
    )
    frequency: Optional[float] = field(
        default=5.5,
        metadata={
            "type": "Element",
        },
    )
    phase: Optional[int] = field(
        default=0,
        metadata={
            "type": "Element",
        },
    )


@dataclass
class Sequence:
    pos: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    path: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )


@dataclass
class InstrumentalTrackBase(abc.ABC):
    name: Optional[str] = field(
        default="神秘立体声_1",
        metadata={
            "name": "Name",
            "type": "Element",
        },
    )
    pan: Optional[float] = field(
        default=0,
        metadata={
            "name": "Pan",
            "type": "Element",
        },
    )
    gain: Optional[float] = field(
        default=0,
        metadata={
            "name": "Gain",
            "type": "Element",
        },
    )
    is_mute: Optional[str] = field(
        default="False",
        metadata={
            "name": "IsMute",
            "type": "Element",
        },
    )
    is_solo: Optional[str] = field(
        default="False",
        metadata={
            "name": "IsSolo",
            "type": "Element",
        },
    )
    sequences: Optional[list[Sequence]] = field(
        default=None,
        metadata={
            "name": "Sequence",
            "type": "Element",
        },
    )


@dataclass
class StereoTrack(InstrumentalTrackBase):
    class Meta:
        name = "StereoTrack"


@dataclass
class MonoTrack(InstrumentalTrackBase):
    class Meta:
        name = "MonoTrack"


@dataclass
class Tempo:
    pos: Optional[int] = field(
        default=0,
        metadata={
            "type": "Element",
        },
    )
    bpm: Optional[float] = field(
        default=120,
        metadata={
            "type": "Element",
        },
    )


@dataclass
class Point:
    class Meta:
        name = "p"

    x: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    y: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )


@dataclass
class Parameter:
    points: list[object] = field(
        default_factory=list,
        metadata=dict(
            type="Wildcard",
            mixed=True,
            choices=(
                {"name": "B", "type": BRE},
                {"name": "D", "type": DYN},
                {"name": "G", "type": GEN},
                {"name": "P", "type": PIT},
                {"name": "R", "type": BRI},
                {"name": "S", "type": STR},
                {"name": "V", "type": VOC},
                {"name": "W", "type": GWL},
                {"name": "X", "type": XSY},
            ),
        ),
    )


@dataclass
class SyllablePartMixin(abc.ABC):
    p: list[Point] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    sample: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    symbol: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )


@dataclass
class SyllableHead(SyllablePartMixin):
    class Meta:
        name = "head"


@dataclass
class SyllableCur(SyllablePartMixin):
    class Meta:
        name = "cur"


@dataclass
class SyllableTail(SyllablePartMixin):
    class Meta:
        name = "tail"


@dataclass
class Syllable:
    head: Optional[SyllableHead] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    cur: Optional[SyllableCur] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    tail: Optional[SyllableTail] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )


@dataclass
class Note:
    pos: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    duration: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    pitch: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    lyric: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    trill: Optional[Trill] = field(
        default=None,
        metadata={
            "name": "trill",
            "type": "Element",
        },
    )
    syllable: Optional[list[Syllable]] = field(
        default_factory=list,
        metadata={
            "name": "Syllable",
            "type": "Element",
        },
    )


@dataclass
class NoteTrack:
    name: Optional[str] = field(
        default="神秘轨道_0",
        metadata={
            "name": "Name",
            "type": "Element",
        },
    )
    singer: Optional[str] = field(
        default="神秘歌手",
        metadata={
            "name": "Singer",
            "type": "Element",
        },
    )
    lsd: Optional[str] = field(
        default=None,
        metadata={
            "name": "LSD",
            "type": "Element",
        },
    )
    pan: Optional[float] = field(
        default=None,
        metadata={
            "name": "Pan",
            "type": "Element",
        },
    )
    gain: Optional[float] = field(
        default=None,
        metadata={
            "name": "Gain",
            "type": "Element",
        },
    )
    is_mute: Optional[str] = field(
        default="False",
        metadata={
            "name": "IsMute",
            "type": "Element",
        },
    )
    is_solo: Optional[str] = field(
        default="False",
        metadata={
            "name": "IsSolo",
            "type": "Element",
        },
    )
    default_parameter: Optional[DefaultParameter] = field(
        default_factory=DefaultParameter,
        metadata={
            "name": "DefaultParameter",
            "type": "Element",
        },
    )
    por: Optional[float] = field(
        default=0.07,
        metadata={
            "type": "Element",
        },
    )
    note: list[Note] = field(
        default_factory=list,
        metadata={
            "name": "Note",
            "type": "Element",
        },
    )
    parameter: Optional[Parameter] = field(
        default=None,
        metadata={
            "name": "Parameter",
            "type": "Element",
        },
    )


@dataclass
class Project:
    samples_per_sec: Optional[int] = field(
        default=44100,
        metadata={
            "name": "SamplesPerSec",
            "type": "Element",
        },
    )
    resolution: Optional[int] = field(
        default=1920,
        metadata={
            "name": "Resolution",
            "type": "Element",
        },
    )
    duration: Optional[int] = field(
        default=None,
        metadata={
            "name": "Duration",
            "type": "Element",
        },
    )
    default_trill: Optional[Trill] = field(
        default_factory=Trill,
        metadata={
            "name": "DefaultTrill",
            "type": "Element",
        },
    )
    tempo: Optional[list[Tempo]] = field(
        default_factory=list,
        metadata={
            "name": "Tempo",
            "type": "Element",
        },
    )
    beat: Optional[list[Beat]] = field(
        default_factory=list,
        metadata={
            "name": "Beat",
            "type": "Element",
        },
    )
    tracks: Optional[list[object]] = field(
        default_factory=list,
        metadata=dict(
            type="Wildcard",
            mixed=True,
            choices=(
                {"name": "NoteTrack", "type": NoteTrack},
                {"name": "StereoTrack", "type": StereoTrack},
                {"name": "MonoTrack", "type": MonoTrack},
            ),
        ),
    )


@dataclass
class VocalSharpProject:
    class Meta:
        name = "VSPX"

    version: Optional[str] = field(
        default="Beta0.0.0",
        metadata={
            "name": "Version",
            "type": "Element",
        },
    )
    project: Optional[Project] = field(
        default_factory=Project,
        metadata={
            "name": "Project",
            "type": "Element",
        },
    )
