import abc
from dataclasses import dataclass, field
from typing import Optional

from libresvip.utils import note2midi


@dataclass
class VocalSharpParamBase(abc.ABC):
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
class BRE(VocalSharpParamBase):
    class Meta:
        name = "B"


@dataclass
class DYN(VocalSharpParamBase):
    class Meta:
        name = "D"


@dataclass
class GEN(VocalSharpParamBase):
    class Meta:
        name = "G"


@dataclass
class PIT(VocalSharpParamBase):
    class Meta:
        name = "P"


@dataclass
class BRI(VocalSharpParamBase):
    class Meta:
        name = "R"


@dataclass
class STR(VocalSharpParamBase):
    class Meta:
        name = "S"


@dataclass
class VOC(VocalSharpParamBase):
    class Meta:
        name = "V"


@dataclass
class GWL(VocalSharpParamBase):
    class Meta:
        name = "W"


@dataclass
class XSY(VocalSharpParamBase):
    class Meta:
        name = "X"


@dataclass
class VocalSharpBeat:
    class Meta:
        name = "Beat"

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
class VocalSharpDefaultParameter:
    class Meta:
        name = "DefaultParameter"

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
class VocalSharpTrillBase(abc.ABC):
    pos: Optional[float] = field(
        default=0.25,
        metadata={
            "type": "Element",
        },
    )
    amplitude: Optional[float] = field(
        default=0,
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
class VocalSharpTrill(VocalSharpTrillBase):
    class Meta:
        name = "trill"


@dataclass
class VocalSharpDefaultTrill(VocalSharpTrillBase):
    class Meta:
        name = "DefaultTrill"


@dataclass
class VocalSharpSequence:
    class Meta:
        name = "Sequence"

    pos: Optional[int] = field(
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
class VocalSharpTrackBase(abc.ABC):
    name: Optional[str] = field(
        default="神秘轨道_0",
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


@dataclass
class VocalSharpInstrumentalTrackBase(VocalSharpTrackBase, abc.ABC):
    sequences: Optional[list[VocalSharpSequence]] = field(
        default_factory=list,
        metadata={
            "name": "Sequence",
            "type": "Element",
        },
    )


@dataclass
class VocalSharpStereoTrack(VocalSharpInstrumentalTrackBase):
    class Meta:
        name = "StereoTrack"


@dataclass
class VocalSharpMonoTrack(VocalSharpInstrumentalTrackBase):
    class Meta:
        name = "MonoTrack"


@dataclass
class VocalSharpTempo:
    class Meta:
        name = "Tempo"

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
class VocalSharpPoint:
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
class VocalSharpParameter:
    class Meta:
        name = "Parameter"

    points: list[object] = field(
        default_factory=list,
        metadata={
            "type": "Wildcard",
            "mixed": True,
            "choices": (
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
        },
    )


@dataclass
class VocalSharpSyllablePartBase(abc.ABC):
    p: list[VocalSharpPoint] = field(
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
class VocalSharpSyllableHead(VocalSharpSyllablePartBase):
    class Meta:
        name = "head"


@dataclass
class VocalSharpSyllableCur(VocalSharpSyllablePartBase):
    class Meta:
        name = "cur"


@dataclass
class VocalSharpSyllableTail(VocalSharpSyllablePartBase):
    class Meta:
        name = "tail"


@dataclass
class VocalSharpSyllable:
    class Meta:
        name = "Syllable"

    head: Optional[VocalSharpSyllableHead] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    cur: Optional[VocalSharpSyllableCur] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    tail: Optional[VocalSharpSyllableTail] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )


@dataclass
class VocalSharpNote:
    class Meta:
        name = "Note"

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
    trill: Optional[VocalSharpTrill] = field(
        default=None,
        metadata={
            "name": "trill",
            "type": "Element",
        },
    )
    syllable: Optional[list[VocalSharpSyllable]] = field(
        default_factory=list,
        metadata={
            "name": "Syllable",
            "type": "Element",
        },
    )

    @property
    def end_pos(self) -> int:
        return self.pos + self.duration

    @property
    def key_number(self) -> int:
        return note2midi(self.pitch)


@dataclass
class VocalSharpNoteTrack(VocalSharpTrackBase):
    class Meta:
        name = "NoteTrack"

    singer: Optional[str] = field(
        default="神秘歌手",
        metadata={
            "name": "Singer",
            "type": "Element",
        },
    )
    lsd: Optional[str] = field(
        default="神秘字典",
        metadata={
            "name": "LSD",
            "type": "Element",
        },
    )
    default_parameter: Optional[VocalSharpDefaultParameter] = field(
        default_factory=VocalSharpDefaultParameter,
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
    note: list[VocalSharpNote] = field(
        default_factory=list,
        metadata={
            "name": "Note",
            "type": "Element",
        },
    )
    parameter: Optional[VocalSharpParameter] = field(
        default_factory=VocalSharpParameter,
        metadata={
            "name": "Parameter",
            "type": "Element",
        },
    )


@dataclass
class VocalSharpInnerProject:
    class Meta:
        name = "Project"

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
    default_trill: Optional[VocalSharpDefaultTrill] = field(
        default_factory=VocalSharpDefaultTrill,
        metadata={
            "name": "DefaultTrill",
            "type": "Element",
        },
    )
    tempo: Optional[list[VocalSharpTempo]] = field(
        default_factory=list,
        metadata={
            "name": "Tempo",
            "type": "Element",
        },
    )
    beat: Optional[list[VocalSharpBeat]] = field(
        default_factory=list,
        metadata={
            "name": "Beat",
            "type": "Element",
        },
    )
    tracks: Optional[list[object]] = field(
        default_factory=list,
        metadata={
            "type": "Elements",
            "choices": (
                {"name": "NoteTrack", "type": VocalSharpNoteTrack},
                {"name": "StereoTrack", "type": VocalSharpStereoTrack},
                {"name": "MonoTrack", "type": VocalSharpMonoTrack},
            ),
        },
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
    project: Optional[VocalSharpInnerProject] = field(
        default_factory=VocalSharpInnerProject,
        metadata={
            "name": "Project",
            "type": "Element",
        },
    )
