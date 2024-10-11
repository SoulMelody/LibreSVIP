import dataclasses
from typing import Union

from construct import (
    Byte,
    Bytes,
    BytesInteger,
    Const,
    GreedyBytes,
    IfThenElse,
    PascalString,
    Prefixed,
    PrefixedArray,
    this,
)
from construct_typed import (
    DataclassMixin,
    DataclassStruct,
    EnumBase,
    TEnum,
    csfield,
)

from .constants import NOTE_UNKNOWN_DATA_BLOCK

Int32ul = BytesInteger(4, swapped=True)
Int32sl = BytesInteger(4, swapped=True, signed=True)


DvBytes = Prefixed(Int32ul, GreedyBytes)
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
    unknown: bytes = csfield(Const(NOTE_UNKNOWN_DATA_BLOCK))
    unknown_phonemes: bytes = csfield(Bytes(18))
    ben_depth: int = csfield(Int32ul)
    ben_length: int = csfield(Int32ul)
    por_tail: int = csfield(Int32ul)
    por_head: int = csfield(Int32ul)
    timbre: int = csfield(Int32sl)
    cross_lyric: str = csfield(DvStr)
    cross_timbre: int = csfield(Int32sl)


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
    unknown_1: list[DvPoint] = csfield(DvParam)
    breath_data: list[DvPoint] = csfield(DvParam)
    gender_data: list[DvPoint] = csfield(DvParam)
    unknown_2: list[DvPoint] = csfield(DvParam)
    unknown_3: list[DvPoint] = csfield(DvParam)


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
    track_data: Union[DvSingingTrack, DvAudioTrack] = csfield(
        IfThenElse(
            this.track_type == DvTrackType.SINGING,
            DataclassStruct(DvSingingTrack),
            DataclassStruct(DvAudioTrack),
        )
    )


@dataclasses.dataclass
class DvInnerProject(DataclassMixin):
    ext_string: bytes = csfield(Const(b"ext1ext2ext3ext4ext5ext6ext7"))
    tempos: list[DvTempo] = csfield(
        Prefixed(Int32ul, PrefixedArray(Int32ul, DataclassStruct(DvTempo)))
    )
    time_signatures: list[DvTimeSignature] = csfield(
        Prefixed(Int32ul, PrefixedArray(Int32ul, DataclassStruct(DvTimeSignature)))
    )
    tracks: list[DvTrack] = csfield(PrefixedArray(Int32ul, DataclassStruct(DvTrack)))


@dataclasses.dataclass
class DvProject(DataclassMixin):
    header: bytes = csfield(Const(b"SHARPKEY\x05\x00\x00\x00"))
    inner_project: DvInnerProject = csfield(Prefixed(Int32ul, DataclassStruct(DvInnerProject)))


dv_project_struct = DataclassStruct(DvProject)
