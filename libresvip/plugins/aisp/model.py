import enum
import itertools
from typing import TYPE_CHECKING, Annotated, Literal, cast

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

if TYPE_CHECKING:
    from collections.abc import Iterable


class AISTrackType(enum.IntEnum):
    TRACK_SING_VOICE = 0
    TRACK_AUDIO = 1
    TRACK_MIDI = 2


class AISNote(BaseModel):
    start: int = Field(alias="s")
    length: int = Field(alias="l")
    midi_no: int = Field(alias="m")
    lyric: str | None = Field(alias="ly")
    pinyin: str | None = Field(alias="py")
    vel: int | None = 50
    triple: bool | None = Field(False, alias="tri")
    pit: list[float] = Field(default_factory=list)
    bc: int | None = 0
    bj: int | None = 0
    bq: int | None = 0

    @field_validator("pit", mode="before")
    @classmethod
    def validate_pit(
        cls, value: str | list[float | str], _info: ValidationInfo
    ) -> list[float] | None:
        if value is None:
            return None
        value_list = value.split() if isinstance(value, str) else value
        pit_list = []
        for x in cast("Iterable[float | str]", value_list):
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
    def serialize_pit(cls, value: list[float] | None, _info: SerializationInfo) -> str:
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
    uid: int | None = None
    start: int = Field(alias="s")
    length: int | None = Field(alias="l")


class AISSingVoicePattern(AISBasePattern):
    notes: list[AISNote] = Field(default_factory=list, alias="n")


class AISAudioPattern(AISBasePattern):
    path_audio: str | None = Field(alias="pa")
    path_wave: str | None = Field(alias="pw")
    n_channel: int | None = 2
    len_sec: int | None = 0


class AISBaseTrack(BaseModel):
    idx: int | None = Field(alias="i")
    solo: bool | None = Field(False, alias="s")
    mute: bool | None = Field(False, alias="m")
    volume: float | None = Field(0, alias="v")
    name: str | None = Field(alias="n")


class AISSingVoiceTrack(AISBaseTrack):
    track_type: Literal[AISTrackType.TRACK_SING_VOICE] = Field(
        AISTrackType.TRACK_SING_VOICE, alias="t"
    )
    singer_namecn: str | None = Field(alias="sn")
    singer_nameen: str | None = Field("", alias="se")
    singer_head_path: str | None = Field("", alias="sh")
    items: list[AISSingVoicePattern] = Field(alias="im", default_factory=list)


class AISAudioTrack(AISBaseTrack):
    track_type: Literal[AISTrackType.TRACK_AUDIO] = Field(AISTrackType.TRACK_AUDIO, alias="t")
    items: list[AISAudioPattern] = Field(alias="im", default_factory=list)


class AISMidiTrack(AISBaseTrack):
    track_type: Literal[AISTrackType.TRACK_MIDI] = Field(AISTrackType.TRACK_MIDI, alias="t")


AISTrack = Annotated[
    AISSingVoiceTrack | AISAudioTrack | AISMidiTrack,
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
    tempo_float: float | None = None
    start_128: int
    start_bar: int
    start_beat_in_bar: int | None = None


class AISProjectBody(BaseModel):
    tracks: list[AISTrack] = Field(default_factory=list)

    @computed_field
    def num_track(self) -> int:
        return len(self.tracks)


class AISProjectHead(BaseModel):
    tempo: list[AISTempo] = Field(default_factory=list)
    signature: list[AISTimeSignature] = Field(default_factory=list)
    flags: int | None = -256
    flage: int | None = -128
    time: int | None = None
    bar: int | None = None
