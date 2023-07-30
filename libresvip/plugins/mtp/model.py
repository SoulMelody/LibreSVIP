import dataclasses
from typing import Optional

from construct import (
    Byte,
    Bytes,
    BytesInteger,
    Const,
    Construct,
    FocusedSeq,
    GreedyBytes,
    GreedyRange,
    If,
    Int16ul,
    PaddedString,
    PascalString,
    Prefixed,
    PrefixedArray,
    this,
)
from construct import Optional as CSOptional
from construct_typed import DataclassMixin, DataclassStruct, EnumBase, TEnum, csfield

Int32ul = BytesInteger(4, swapped=True)
Int32sl = BytesInteger(4, swapped=True, signed=True)
LineBreak = Const(b"\n")


def muta_prefixed_array(data_model: DataclassMixin) -> Construct:
    return PrefixedArray(
        FocusedSeq("count", "count" / Int32ul, LineBreak),
        DataclassStruct(data_model),
    )


class MutaTrackType(EnumBase):
    TALK = 1
    SONG = 2
    AUDIO = 3


@dataclasses.dataclass
class MutaTempo(DataclassMixin):
    position: int = csfield(Int32ul)
    bpm: int = csfield(Int32ul)


@dataclasses.dataclass
class MutaTimeSignature(DataclassMixin):
    measure_position: int = csfield(Int32ul)
    numerator: int = csfield(Int32ul)
    denominator: int = csfield(Int32ul)


@dataclasses.dataclass
class MutaAudioTrackData(DataclassMixin):
    start: int = csfield(Int32ul)
    length: int = csfield(Int32ul)
    file_path: str = csfield(PascalString(Int32ul, "utf-8"))
    line_break: bytes = csfield(LineBreak)


@dataclasses.dataclass
class MutaNoteTiming(DataclassMixin):
    ori_pos: int = csfield(Int32sl)
    mod_pos: int = csfield(Int32sl)


@dataclasses.dataclass
class MutaNote(DataclassMixin):
    start: int = csfield(Int32ul)
    length: int = csfield(Int32ul)
    key: int = csfield(Int32ul)
    lyric: list[int] = csfield(Int16ul[8])
    phoneme: str = csfield(PaddedString(16, "utf-16-le"))
    tmg_data: list[MutaNoteTiming] = csfield(DataclassStruct(MutaNoteTiming)[5])
    line_break: bytes = csfield(LineBreak)


@dataclasses.dataclass
class MutaPoint(DataclassMixin):
    time: int = csfield(Int32sl)
    value: int = csfield(Int32ul)
    line_break: bytes = csfield(LineBreak)


MutaPoints = muta_prefixed_array(MutaPoint)


@dataclasses.dataclass
class MutaParams(DataclassMixin):
    unknown_param: list[MutaPoint] = csfield(MutaPoints)
    pitch_range: list[MutaPoint] = csfield(MutaPoints)
    pitch_data: list[MutaPoint] = csfield(MutaPoints)
    volume_data: list[MutaPoint] = csfield(MutaPoints)
    vibrato_amplitude_range: list[MutaPoint] = csfield(MutaPoints)
    vibrato_amplitude_data: list[MutaPoint] = csfield(MutaPoints)
    vibrato_frequency_range: list[MutaPoint] = csfield(MutaPoints)
    vibrato_frequency_data: list[MutaPoint] = csfield(MutaPoints)


@dataclasses.dataclass
class MutaSongTrackData(DataclassMixin):
    start: int = csfield(Int32ul)
    length: int = csfield(Int32ul)
    singer_name: list[int] = csfield(Int16ul[258])
    unknown_1: int = csfield(Int32ul)
    line_break1: bytes = csfield(LineBreak)
    notes: list[MutaNote] = csfield(muta_prefixed_array(MutaNote))
    params: MutaParams = csfield(DataclassStruct(MutaParams))


@dataclasses.dataclass
class MutaPhoneme(DataclassMixin):
    volume: int = csfield(Byte)
    pos1: int = csfield(Int16ul)
    length: int = csfield(Byte)
    pos2: int = csfield(Int16ul)
    pitch: int = csfield(Int32ul)
    phoneme: bytes = csfield(Prefixed(Int32ul, GreedyBytes))
    line_break: bytes = csfield(LineBreak)


@dataclasses.dataclass
class MutaText(DataclassMixin):
    text: bytes = csfield(Prefixed(Int32ul, GreedyBytes))
    line_break1: bytes = csfield(LineBreak)
    volume: int = csfield(Byte)
    speed: int = csfield(Byte)
    tone: int = csfield(Byte)
    quality: int = csfield(Byte)
    normal: int = csfield(Byte)
    happiness: int = csfield(Byte)
    sadness: int = csfield(Byte)
    reserved: int = csfield(Byte)
    line_break2: bytes = csfield(LineBreak)
    phonemes: list[MutaPhoneme] = csfield(muta_prefixed_array(MutaPhoneme))


@dataclasses.dataclass
class MutaTalkTrackData(DataclassMixin):
    start: int = csfield(Int32ul)
    length: int = csfield(Int32ul)
    talker_name: list[int] = csfield(Int16ul[258])
    unknown_1: int = csfield(Int32ul)
    line_break: bytes = csfield(LineBreak)
    text: MutaText = csfield(DataclassStruct(MutaText))


@dataclasses.dataclass
class MutaTrack(DataclassMixin):
    track_type: MutaTrackType = csfield(TEnum(Int32ul, MutaTrackType))
    track_index: int = csfield(Int32ul)
    line_break: bytes = csfield(LineBreak)
    mute: int = csfield(Int32ul)
    solo: int = csfield(Int32ul)
    volume: int = csfield(Int32ul)
    pan: int = csfield(Int32ul)
    name: str = csfield(PaddedString(12, "utf-16-le"))
    padding: bytes = csfield(Bytes(53))
    talk_track_data: Optional[list[MutaTalkTrackData]] = csfield(
        If(
            this.track_type == MutaTrackType.TALK,
            GreedyRange(DataclassStruct(MutaTalkTrackData)),
        )
    )
    audio_track_data: Optional[MutaAudioTrackData] = csfield(
        If(
            this.track_type == MutaTrackType.AUDIO,
            CSOptional(DataclassStruct(MutaAudioTrackData)),
        )
    )
    song_track_data: Optional[MutaSongTrackData] = csfield(
        If(this.track_type == MutaTrackType.SONG, DataclassStruct(MutaSongTrackData))
    )


@dataclasses.dataclass
class MutaProject(DataclassMixin):
    file_version: int = csfield(Int32ul)
    line_break1: bytes = csfield(LineBreak)
    tempos: list[MutaTempo] = csfield(muta_prefixed_array(MutaTempo))
    line_break2: bytes = csfield(LineBreak)
    time_signatures: list[MutaTimeSignature] = csfield(
        muta_prefixed_array(MutaTimeSignature)
    )
    line_break3: bytes = csfield(LineBreak)
    tracks: list[MutaTrack] = csfield(muta_prefixed_array(MutaTrack))


muta_project_struct = DataclassStruct(MutaProject)
