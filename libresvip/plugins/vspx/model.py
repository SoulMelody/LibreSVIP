import abc

from xsdata_pydantic.fields import field

from libresvip.model.base import BaseModel
from libresvip.utils.music_math import note2midi


class VocalSharpParamBase(abc.ABC, BaseModel):
    time: int = field(
        metadata={
            "name": "t",
            "type": "Element",
        },
    )
    value: int = field(
        metadata={
            "name": "v",
            "type": "Element",
        },
    )


class BRE(VocalSharpParamBase):
    class Meta:
        name = "B"


class DYN(VocalSharpParamBase):
    class Meta:
        name = "D"


class GEN(VocalSharpParamBase):
    class Meta:
        name = "G"


class PIT(VocalSharpParamBase):
    class Meta:
        name = "P"


class BRI(VocalSharpParamBase):
    class Meta:
        name = "R"


class STR(VocalSharpParamBase):
    class Meta:
        name = "S"


class VOC(VocalSharpParamBase):
    class Meta:
        name = "V"


class GWL(VocalSharpParamBase):
    class Meta:
        name = "W"


class XSY(VocalSharpParamBase):
    class Meta:
        name = "X"


class VocalSharpBeat(BaseModel):
    class Meta:
        name = "Beat"

    bar_index: int | None = field(
        default=0,
        metadata={
            "name": "barIndex",
            "type": "Element",
        },
    )
    beat_per_bar: int | None = field(
        default=4,
        metadata={
            "name": "beatPerBar",
            "type": "Element",
        },
    )
    bar_divide: int | None = field(
        default=4,
        metadata={
            "name": "barDivide",
            "type": "Element",
        },
    )


class VocalSharpDefaultParameter(BaseModel):
    class Meta:
        name = "DefaultParameter"

    dyn: int | None = field(
        default=128,
        metadata={
            "type": "Element",
        },
    )
    strength: int | None = field(
        default=128,
        metadata={
            "name": "str",
            "type": "Element",
        },
    )
    bri: int | None = field(
        default=128,
        metadata={
            "type": "Element",
        },
    )
    voc: int | None = field(
        default=255,
        metadata={
            "type": "Element",
        },
    )
    bre: int | None = field(
        default=128,
        metadata={
            "type": "Element",
        },
    )
    gen: int | None = field(
        default=128,
        metadata={
            "type": "Element",
        },
    )
    gwl: int | None = field(
        default=0,
        metadata={
            "type": "Element",
        },
    )
    xsy: int | None = field(
        default=0,
        metadata={
            "type": "Element",
        },
    )


class VocalSharpTrillBase(abc.ABC, BaseModel):
    pos: float = field(
        default=0.25,
        metadata={
            "type": "Element",
        },
    )
    amplitude: float = field(
        default=0,
        metadata={
            "type": "Element",
        },
    )
    frequency: float = field(
        default=5.5,
        metadata={
            "type": "Element",
        },
    )
    phase: float = field(
        default=0,
        metadata={
            "type": "Element",
        },
    )


class VocalSharpTrill(VocalSharpTrillBase):
    class Meta:
        name = "trill"


class VocalSharpDefaultTrill(VocalSharpTrillBase):
    class Meta:
        name = "DefaultTrill"


class VocalSharpSequence(BaseModel):
    class Meta:
        name = "Sequence"

    pos: int | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    name: str | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    path: str | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )


class VocalSharpTrackBase(abc.ABC, BaseModel):
    name: str | None = field(
        default="神秘轨道_0",
        metadata={
            "name": "Name",
            "type": "Element",
        },
    )
    pan: float | None = field(
        default=0,
        metadata={
            "name": "Pan",
            "type": "Element",
        },
    )
    gain: float | None = field(
        default=0,
        metadata={
            "name": "Gain",
            "type": "Element",
        },
    )
    is_mute: str | None = field(
        default="False",
        metadata={
            "name": "IsMute",
            "type": "Element",
        },
    )
    is_solo: str | None = field(
        default="False",
        metadata={
            "name": "IsSolo",
            "type": "Element",
        },
    )


class VocalSharpInstrumentalTrackBase(VocalSharpTrackBase, abc.ABC):
    sequences: list[VocalSharpSequence] = field(
        default_factory=list,
        metadata={
            "name": "Sequence",
            "type": "Element",
        },
    )


class VocalSharpStereoTrack(VocalSharpInstrumentalTrackBase):
    class Meta:
        name = "StereoTrack"


class VocalSharpMonoTrack(VocalSharpInstrumentalTrackBase):
    class Meta:
        name = "MonoTrack"


class VocalSharpTempo(BaseModel):
    class Meta:
        name = "Tempo"

    pos: int | None = field(
        default=0,
        metadata={
            "type": "Element",
        },
    )
    bpm: float | None = field(
        default=120,
        metadata={
            "type": "Element",
        },
    )


class VocalSharpPoint(BaseModel):
    class Meta:
        name = "p"

    x: float | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    y: float | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )


class VocalSharpParameter(BaseModel):
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


class VocalSharpSyllablePartBase(abc.ABC, BaseModel):
    p: list[VocalSharpPoint] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    sample: str | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    symbol: str | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )


class VocalSharpSyllableHead(VocalSharpSyllablePartBase):
    class Meta:
        name = "head"


class VocalSharpSyllableCur(VocalSharpSyllablePartBase):
    class Meta:
        name = "cur"


class VocalSharpSyllableTail(VocalSharpSyllablePartBase):
    class Meta:
        name = "tail"


class VocalSharpSyllable(BaseModel):
    class Meta:
        name = "Syllable"

    head: VocalSharpSyllableHead | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    cur: VocalSharpSyllableCur | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    tail: VocalSharpSyllableTail | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )


class VocalSharpNote(BaseModel):
    class Meta:
        name = "Note"

    pitch: str = field(
        metadata={
            "type": "Element",
        },
    )
    pos: int = field(
        metadata={
            "type": "Element",
        },
    )
    duration: int = field(
        metadata={
            "type": "Element",
        },
    )
    lyric: str | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    trill: VocalSharpTrill | None = field(
        default=None,
        metadata={
            "name": "trill",
            "type": "Element",
        },
    )
    syllable: list[VocalSharpSyllable] = field(
        default_factory=list,
        metadata={
            "name": "Syllable",
            "type": "Element",
        },
    )

    @property
    def key_number(self) -> int:
        return note2midi(self.pitch)


class VocalSharpNoteTrack(VocalSharpTrackBase):
    class Meta:
        name = "NoteTrack"

    singer: str | None = field(
        default="神秘歌手",
        metadata={
            "name": "Singer",
            "type": "Element",
        },
    )
    lsd: str | None = field(
        default="神秘字典",
        metadata={
            "name": "LSD",
            "type": "Element",
        },
    )
    default_parameter: VocalSharpDefaultParameter | None = field(
        default_factory=VocalSharpDefaultParameter,
        metadata={
            "name": "DefaultParameter",
            "type": "Element",
        },
    )
    por: float = field(
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
    parameter: VocalSharpParameter = field(
        default_factory=VocalSharpParameter,
        metadata={
            "name": "Parameter",
            "type": "Element",
        },
    )


class VocalSharpInnerProject(BaseModel):
    class Meta:
        name = "Project"

    samples_per_sec: int | None = field(
        default=44100,
        metadata={
            "name": "SamplesPerSec",
            "type": "Element",
        },
    )
    resolution: int | None = field(
        default=1920,
        metadata={
            "name": "Resolution",
            "type": "Element",
        },
    )
    duration: int | None = field(
        default=None,
        metadata={
            "name": "Duration",
            "type": "Element",
        },
    )
    default_trill: VocalSharpDefaultTrill | None = field(
        default_factory=VocalSharpDefaultTrill,
        metadata={
            "name": "DefaultTrill",
            "type": "Element",
        },
    )
    tempo: list[VocalSharpTempo] = field(
        default_factory=list,
        metadata={
            "name": "Tempo",
            "type": "Element",
        },
    )
    beat: list[VocalSharpBeat] = field(
        default_factory=list,
        metadata={
            "name": "Beat",
            "type": "Element",
        },
    )
    tracks: list[object] = field(
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


class VocalSharpProject(BaseModel):
    class Meta:
        name = "VSPX"

    version: str | None = field(
        default="Beta0.0.0",
        metadata={
            "name": "Version",
            "type": "Element",
        },
    )
    project: VocalSharpInnerProject = field(
        default_factory=VocalSharpInnerProject,
        metadata={
            "name": "Project",
            "type": "Element",
        },
    )
