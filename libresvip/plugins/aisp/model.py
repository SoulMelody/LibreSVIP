import enum
import itertools
from collections.abc import Iterable
from typing import Annotated, Literal, Optional, Union, cast

import more_itertools
from pydantic import (
    Field,
    SerializationInfo,
    ValidationInfo,
    computed_field,
    field_serializer,
    field_validator,
)

from libresvip.model.base import BaseModel


class AISTrackType(enum.IntEnum):
    TRACK_SING_VOICE = 0
    TRACK_AUDIO = 1
    TRACK_MIDI = 2


class AISNote(BaseModel):
    start: int = Field(alias="s")
    length: int = Field(alias="l")
    midi_no: int = Field(alias="m")
    lyric: Optional[str] = Field(alias="ly")
    pinyin: Optional[str] = Field(alias="py")
    vel: Optional[int] = 50
    triple: Optional[bool] = Field(False, alias="tri")
    pit: list[float] = Field(default_factory=list)
    bc: Optional[int] = 0
    bj: Optional[int] = 0
    bq: Optional[int] = 0

    @field_validator("pit", mode="before")
    @classmethod
    def validate_pit(
        cls, value: Union[str, list[Union[float, str]]], _info: ValidationInfo
    ) -> Optional[list[float]]:
        if value is None:
            return None
        value_list = value.split() if isinstance(value, str) else value
        pit_list = []
        for x in cast(Iterable[Union[float, str]], value_list):
            if isinstance(x, str) and "x" in x:
                x, _, repeat_times = x.partition("x")
                pit_list.extend([float(x)] * int(repeat_times))
            elif isinstance(x, str):
                pit_list.append(float(x))
            else:
                pit_list.append(x)
        return pit_list

    @field_serializer("pit", when_used="json-unless-none")
    @classmethod
    def serialize_pit(cls, value: Optional[list[float]], _info: SerializationInfo) -> str:
        if value is None:
            return "0x500"
        pit_str = ""
        for key, group in itertools.groupby(value):
            group_length = more_itertools.ilen(group)
            pit_str += (
                f"{round(key, 2)}x{group_length} " if group_length > 1 else f"{round(key, 2)} "
            )
        return pit_str.strip()


class AISBasePattern(BaseModel):
    uid: Optional[int] = None
    start: int = Field(alias="s")
    length: Optional[int] = Field(alias="l")


class AISSingVoicePattern(AISBasePattern):
    notes: list[AISNote] = Field(default_factory=list, alias="n")


class AISAudioPattern(AISBasePattern):
    path_audio: Optional[str] = Field(alias="pa")
    path_wave: Optional[str] = Field(alias="pw")
    n_channel: Optional[int] = 2
    len_sec: Optional[int] = 0


class AISBaseTrack(BaseModel):
    idx: Optional[int] = Field(alias="i")
    solo: Optional[bool] = Field(False, alias="s")
    mute: Optional[bool] = Field(False, alias="m")
    volume: Optional[float] = Field(0, alias="v")
    name: Optional[str] = Field(alias="n")


class AISSingVoiceTrack(AISBaseTrack):
    track_type: Literal[AISTrackType.TRACK_SING_VOICE] = Field(
        AISTrackType.TRACK_SING_VOICE, alias="t"
    )
    singer_namecn: Optional[str] = Field(alias="sn")
    singer_nameen: Optional[str] = Field("", alias="se")
    singer_head_path: Optional[str] = Field("", alias="sh")
    items: list[AISSingVoicePattern] = Field(alias="im", default_factory=list)


class AISAudioTrack(AISBaseTrack):
    track_type: Literal[AISTrackType.TRACK_AUDIO] = Field(AISTrackType.TRACK_AUDIO, alias="t")
    items: list[AISAudioPattern] = Field(alias="im", default_factory=list)


class AISMidiTrack(AISBaseTrack):
    track_type: Literal[AISTrackType.TRACK_MIDI] = Field(AISTrackType.TRACK_MIDI, alias="t")


AISTrack = Annotated[
    Union[AISSingVoiceTrack, AISAudioTrack, AISMidiTrack],
    Field(discriminator="track_type"),
]


class AISTimeSignature(BaseModel):
    beat_zi: int = 4
    beat_mu: int = 4
    start_bar: int = 0

    @computed_field(alias="str")
    def str_value(self) -> str:
        return f"{self.beat_zi}/{self.beat_mu}"


class AISTempo(BaseModel):
    tempo_float: Optional[float] = None
    start_128: int
    start_bar: int
    start_beat_in_bar: Optional[int] = None


class AISProjectBody(BaseModel):
    tracks: list[AISTrack] = Field(default_factory=list)

    @computed_field
    def num_track(self) -> int:
        return len(self.tracks)


class AISProjectHead(BaseModel):
    tempo: list[AISTempo] = Field(default_factory=list)
    signature: list[AISTimeSignature] = Field(default_factory=list)
    flags: Optional[int] = -256
    flage: Optional[int] = -128
    time: Optional[int] = None
    bar: Optional[int] = None
