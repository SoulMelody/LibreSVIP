import dataclasses
from typing import List, Optional

from construct import (
    Bytes,
    BytesInteger,
    Const,
    If,
    Int16ul,
    PaddedString,
    Padding,
    PascalString,
    this,
)
from construct import Optional as CSOptional
from construct_typed import DataclassMixin, DataclassStruct, EnumBase, TEnum, csfield

Int32ul = BytesInteger(4, swapped=True)
LineBreak = Const(b"\n")


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
    end: int = csfield(Int32ul)
    file_path: str = csfield(PascalString(Int32ul, "utf-8"))
    line_break: bytes = csfield(LineBreak)


@dataclasses.dataclass
class MutaNote(DataclassMixin):
    start: int = csfield(Int32ul)
    length: int = csfield(Int32ul)
    key: int = csfield(Int32ul)
    lyric: str = csfield(Int16ul[8])
    phoneme: str = csfield(PaddedString(16, "utf-16-le"))
    tmg_data: bytes = csfield(Bytes(40))
    line_break: bytes = csfield(LineBreak)


@dataclasses.dataclass
class MutaPoint(DataclassMixin):
    time: int = csfield(Int32ul)
    value: int = csfield(Int32ul)
    line_break: bytes = csfield(LineBreak)


@dataclasses.dataclass
class MutaPoints(DataclassMixin):
    count: int = csfield(Int32ul)
    line_break: bytes = csfield(LineBreak)
    points: List[MutaPoint] = csfield(DataclassStruct(MutaPoint)[this.count])


@dataclasses.dataclass
class MutaParams(DataclassMixin):
    unknown_param: MutaPoints = csfield(DataclassStruct(MutaPoints))
    pitch_range: MutaPoints = csfield(DataclassStruct(MutaPoints))
    pitch_data: MutaPoints = csfield(DataclassStruct(MutaPoints))
    volume_data: MutaPoints = csfield(DataclassStruct(MutaPoints))
    vibrato_amplitude_range: MutaPoints = csfield(DataclassStruct(MutaPoints))
    vibrato_amplitude_data: MutaPoints = csfield(DataclassStruct(MutaPoints))
    vibrato_frequency_range: MutaPoints = csfield(DataclassStruct(MutaPoints))
    vibrato_frequency_data: MutaPoints = csfield(DataclassStruct(MutaPoints))


@dataclasses.dataclass
class MutaSongTrackData(DataclassMixin):
    start: int = csfield(Int32ul)
    end: int = csfield(Int32ul)
    singer_name: str = csfield(Int16ul[258])
    unknown_1: int = csfield(Int32ul)
    line_break1: bytes = csfield(LineBreak)
    note_count: int = csfield(Int32ul)
    line_break2: bytes = csfield(LineBreak)
    notes: List[MutaNote] = csfield(DataclassStruct(MutaNote)[this.note_count])
    params: List[MutaParams] = csfield(DataclassStruct(MutaParams))


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
    padding: bytes = csfield(Padding(53))
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
    file_size: int = csfield(Int32ul)
    line_break1: bytes = csfield(LineBreak)
    tempo_count: int = csfield(Int32ul)
    line_break2: bytes = csfield(LineBreak)
    tempos: List[MutaTempo] = csfield(DataclassStruct(MutaTempo)[this.tempo_count])
    line_break3: bytes = csfield(LineBreak)
    time_signature_count: int = csfield(Int32ul)
    line_break4: bytes = csfield(LineBreak)
    time_signatures: List[MutaTimeSignature] = csfield(
        DataclassStruct(MutaTimeSignature)[this.time_signature_count]
    )
    line_break5: bytes = csfield(LineBreak)
    track_count: int = csfield(Int32ul)
    line_break6: bytes = csfield(LineBreak)
    tracks: List[MutaTrack] = csfield(DataclassStruct(MutaTrack)[this.track_count])


muta_project = DataclassStruct(MutaProject)
