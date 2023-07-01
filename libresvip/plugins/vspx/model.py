import abc
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class VSPXParamMixin(abc.ABC):
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
class BRE(VSPXParamMixin):
    class Meta:
        name = "B"


@dataclass
class DYN(VSPXParamMixin):
    class Meta:
        name = "D"


@dataclass
class GEN(VSPXParamMixin):
    class Meta:
        name = "G"


@dataclass
class PIT(VSPXParamMixin):
    class Meta:
        name = "P"


@dataclass
class BRI(VSPXParamMixin):
    class Meta:
        name = "R"


@dataclass
class STR(VSPXParamMixin):
    class Meta:
        name = "S"


@dataclass
class VOC(VSPXParamMixin):
    class Meta:
        name = "V"


@dataclass
class GWL(VSPXParamMixin):
    class Meta:
        name = "W"


@dataclass
class XSY(VSPXParamMixin):
    class Meta:
        name = "X"


@dataclass
class Beat:
    bar_index: Optional[int] = field(
        default=None,
        metadata={
            "name": "barIndex",
            "type": "Element",
        },
    )
    beat_per_bar: Optional[int] = field(
        default=None,
        metadata={
            "name": "beatPerBar",
            "type": "Element",
        },
    )
    bar_divide: Optional[int] = field(
        default=None,
        metadata={
            "name": "barDivide",
            "type": "Element",
        },
    )


@dataclass
class DefaultParameter:
    dyn: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    strength: Optional[int] = field(
        default=None,
        metadata={
            "name": "str",
            "type": "Element",
        },
    )
    bri: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    voc: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    bre: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    gen: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    gwl: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    xsy: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )


@dataclass
class Trill:
    pos: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    amplitude: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    frequency: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    phase: Optional[int] = field(
        default=None,
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
class InstrumentalTrack:
    name: Optional[str] = field(
        default=None,
        metadata={
            "name": "Name",
            "type": "Element",
        },
    )
    pan: Optional[int] = field(
        default=None,
        metadata={
            "name": "Pan",
            "type": "Element",
        },
    )
    gain: Optional[int] = field(
        default=None,
        metadata={
            "name": "Gain",
            "type": "Element",
        },
    )
    is_mute: Optional[str] = field(
        default=None,
        metadata={
            "name": "IsMute",
            "type": "Element",
        },
    )
    is_solo: Optional[str] = field(
        default=None,
        metadata={
            "name": "IsSolo",
            "type": "Element",
        },
    )
    sequences: list[Sequence] = field(
        default_factory=list,
        metadata={
            "name": "Sequence",
            "type": "Element",
        },
    )


@dataclass
class Tempo:
    pos: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    bpm: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )


@dataclass
class Point:
    class Meta:
        name = "p"

    x: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    y: Optional[int] = field(
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
        default=None,
        metadata={
            "name": "Name",
            "type": "Element",
        },
    )
    singer: Optional[str] = field(
        default=None,
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
    pan: Optional[int] = field(
        default=None,
        metadata={
            "name": "Pan",
            "type": "Element",
        },
    )
    gain: Optional[int] = field(
        default=None,
        metadata={
            "name": "Gain",
            "type": "Element",
        },
    )
    is_mute: Optional[str] = field(
        default=None,
        metadata={
            "name": "IsMute",
            "type": "Element",
        },
    )
    is_solo: Optional[str] = field(
        default=None,
        metadata={
            "name": "IsSolo",
            "type": "Element",
        },
    )
    default_parameter: Optional[DefaultParameter] = field(
        default=None,
        metadata={
            "name": "DefaultParameter",
            "type": "Element",
        },
    )
    por: Optional[float] = field(
        default=None,
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
        default=None,
        metadata={
            "name": "SamplesPerSec",
            "type": "Element",
        },
    )
    resolution: Optional[int] = field(
        default=None,
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
        default=None,
        metadata={
            "name": "DefaultTrill",
            "type": "Element",
        },
    )
    tempo: Optional[list[Tempo]] = field(
        default=None,
        metadata={
            "name": "Tempo",
            "type": "Element",
        },
    )
    beat: Optional[list[Beat]] = field(
        default=None,
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
                {"name": "StereoTrack", "type": InstrumentalTrack},
                {"name": "MonoTrack", "type": InstrumentalTrack},
            ),
        ),
    )


@dataclass
class VocalSharpProject:
    class Meta:
        name = "VSPX"

    version: Optional[str] = field(
        default=None,
        metadata={
            "name": "Version",
            "type": "Element",
        },
    )
    project: Optional[Project] = field(
        default=None,
        metadata={
            "name": "Project",
            "type": "Element",
        },
    )
