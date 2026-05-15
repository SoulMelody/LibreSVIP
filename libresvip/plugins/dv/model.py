import dataclasses

from construct import (
    Byte,
    BytesInteger,
    Const,
    Default,
    Float32l,
    IfThenElse,
    Int8sl,
    PascalString,
    Prefixed,
    PrefixedArray,
    Sequence,
    this,
)
from construct import Optional as CSOptional
from construct_typed import (
    Context,
    DataclassMixin,
    DataclassStruct,
    EnumBase,
    TEnum,
    csfield,
)

from libresvip.utils.binary import Null

Int32ul = BytesInteger(4, swapped=True)
Int32sl = BytesInteger(4, swapped=True, signed=True)


def _has_feature(ctx: Context, feature: str) -> bool:
    feature_bytes = feature.encode("utf-8")
    while ctx is not None:
        if hasattr(ctx, "features"):
            return feature_bytes in ctx.get("features")
        ctx = ctx.get("_") if hasattr(ctx, "get") else None
    return False


DvStr = PascalString(Int32ul, "utf-8")


@dataclasses.dataclass
class DvPoint(DataclassMixin):
    x: int = csfield(Int32sl)
    y: int = csfield(Int32sl)


DvParam = Prefixed(Int32ul, PrefixedArray(Int32ul, DataclassStruct(DvPoint)))


@dataclasses.dataclass
class DvTempo(DataclassMixin):
    position: int = csfield(Int32sl)
    bpm: int = csfield(Int32ul)


@dataclasses.dataclass
class DvTimeSignature(DataclassMixin):
    measure_position: int = csfield(Int32sl)
    numerator: int = csfield(Int32ul)
    denominator: int = csfield(Int32ul)


@dataclasses.dataclass
class DvNoteParameter(DataclassMixin):
    amplitude_points: list[DvPoint] = csfield(DvParam)
    frequency_points: list[DvPoint] = csfield(DvParam)
    vibrato_points: list[DvPoint] = csfield(DvParam)


@dataclasses.dataclass
class DvPhoneme(DataclassMixin):
    unknown_1: int = csfield(Int8sl)
    consonant_rate: float = csfield(Float32l)
    vowel_modified: int = csfield(Int8sl)
    medial: float = csfield(Float32l)
    rime: float = csfield(Float32l)
    ending: float = csfield(Float32l)


@dataclasses.dataclass
class DvNote(DataclassMixin):
    start: int = csfield(Int32sl)
    length: int = csfield(Int32ul)
    key: int = csfield(Int32ul)
    vibrato: int = csfield(Int32ul)
    phoneme: str = csfield(DvStr)
    word: str = csfield(DvStr)
    padding_1: int = csfield(Byte)
    note_vibrato_data: DvNoteParameter = csfield(
        Prefixed(Int32ul, DataclassStruct(DvNoteParameter))
    )
    unknown: tuple[float, ...] = csfield(Prefixed(Int32ul, PrefixedArray(Int32ul, Float32l)))
    phonemes: DvPhoneme | None = csfield(
        IfThenElse(lambda this: _has_feature(this, "ext1"), DataclassStruct(DvPhoneme), Null)
    )
    ben_depth: int | None = csfield(
        IfThenElse(lambda this: _has_feature(this, "ext2"), Int32ul, Null)
    )
    ben_length: int | None = csfield(
        IfThenElse(lambda this: _has_feature(this, "ext2"), Int32ul, Null)
    )
    por_tail: int | None = csfield(
        IfThenElse(lambda this: _has_feature(this, "ext2"), Int32ul, Null)
    )
    por_head: int | None = csfield(
        IfThenElse(lambda this: _has_feature(this, "ext2"), Int32ul, Null)
    )
    timbre: int | None = csfield(IfThenElse(lambda this: _has_feature(this, "ext4"), Int32sl, Null))
    cross_lyric: str | None = csfield(
        IfThenElse(lambda this: _has_feature(this, "ext7"), DvStr, Null)
    )
    cross_timbre: int | None = csfield(
        IfThenElse(lambda this: _has_feature(this, "ext7"), Int32sl, Null)
    )


@dataclasses.dataclass
class DvSegment(DataclassMixin):
    start: int = csfield(Int32ul)
    length: int = csfield(Int32ul)
    name: str = csfield(DvStr)
    singer_name: str = csfield(DvStr)
    notes: list[DvNote] = csfield(
        Prefixed(Int32ul, PrefixedArray(Int32ul, DataclassStruct(DvNote)))
    )
    volume_data: list[DvPoint] = csfield(DvParam)
    pitch_data: list[DvPoint] = csfield(DvParam)
    breath_data: list[DvPoint] = csfield(DvParam)
    ext3_data: list[DvPoint] | None = csfield(
        IfThenElse(lambda this: _has_feature(this, "ext3"), DvParam, Null)
    )
    ext5_data: list[DvPoint] | None = csfield(
        IfThenElse(lambda this: _has_feature(this, "ext5"), DvParam, Null)
    )
    ext6_data: list[DvPoint] | None = csfield(
        IfThenElse(lambda this: _has_feature(this, "ext6"), DvParam, Null)
    )
    ext7_data: list[DvPoint] | None = csfield(
        IfThenElse(lambda this: _has_feature(this, "ext7"), DvParam, Null)
    )


@dataclasses.dataclass
class DvSingingTrack(DataclassMixin):
    name: str = csfield(DvStr)
    mute: int = csfield(Byte)
    solo: int = csfield(Byte)
    volume: int = csfield(Int32ul)
    balance: int = csfield(Int32ul)
    segments: list[DvSegment] = csfield(
        Prefixed(Int32ul, PrefixedArray(Int32ul, DataclassStruct(DvSegment)))
    )


@dataclasses.dataclass
class DvAudioInfo(DataclassMixin):
    start: int = csfield(Int32ul)
    length: int = csfield(Int32ul)
    name: str = csfield(DvStr)
    path: str = csfield(DvStr)


@dataclasses.dataclass
class DvAudioTrack(DataclassMixin):
    name: str = csfield(DvStr)
    mute: int = csfield(Byte)
    solo: int = csfield(Byte)
    volume: int = csfield(Int32ul)
    balance: int = csfield(Int32ul)
    infos: list[DvAudioInfo] = csfield(
        Prefixed(Int32ul, PrefixedArray(Int32ul, DataclassStruct(DvAudioInfo)))
    )


class DvTrackType(EnumBase):
    SINGING = 0
    AUDIO = 1


@dataclasses.dataclass
class DvTrack(DataclassMixin):
    track_type: DvTrackType = csfield(TEnum(Int32ul, DvTrackType))
    track_data: DvSingingTrack | DvAudioTrack = csfield(
        IfThenElse(
            this.track_type == DvTrackType.SINGING,
            DataclassStruct(DvSingingTrack),
            DataclassStruct(DvAudioTrack),
        )
    )


@dataclasses.dataclass
class DvInnerProject(DataclassMixin):
    features: list[bytes | None] = csfield(
        Sequence(
            Default(CSOptional(Const(b"ext1")), b"ext1"),
            Default(CSOptional(Const(b"ext2")), b"ext2"),
            Default(CSOptional(Const(b"ext3")), b"ext3"),
            Default(CSOptional(Const(b"ext4")), b"ext4"),
            Default(CSOptional(Const(b"ext5")), b"ext5"),
            Default(CSOptional(Const(b"ext6")), b"ext6"),
            Default(CSOptional(Const(b"ext7")), b"ext7"),
        )
    )
    tempos: list[DvTempo] = csfield(
        Prefixed(Int32ul, PrefixedArray(Int32ul, DataclassStruct(DvTempo)))
    )
    time_signatures: list[DvTimeSignature] = csfield(
        Prefixed(Int32ul, PrefixedArray(Int32ul, DataclassStruct(DvTimeSignature)))
    )
    tracks: list[DvTrack] = csfield(PrefixedArray(Int32ul, DataclassStruct(DvTrack)))


@dataclasses.dataclass
class DvProject(DataclassMixin):
    magic: bytes = csfield(Const(b"SHARPKEY"))
    version: int = csfield(Int32ul)
    inner_project: DvInnerProject = csfield(Prefixed(Int32ul, DataclassStruct(DvInnerProject)))


dv_project_struct = DataclassStruct(DvProject)
