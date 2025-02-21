from enum import Enum

from pydantic import Field

from libresvip.core.constants import TICKS_IN_BEAT
from libresvip.model.base import BaseModel


class GjgjBeatStyle(Enum):
    NONE = 0
    SP = 1
    SIL = 2


class GjgjBeatItems(BaseModel):
    id_value: int | None = Field(alias="ID")
    lyric: str = Field(alias="Lyric")
    pinyin: str = Field(alias="Pinyin")
    start_tick: int = Field(alias="StartTick")
    duration: int = Field(alias="Duration")
    track: int | None = Field(alias="Track")
    pre_time: float = Field(0.0, alias="PreTime")
    post_time: float = Field(0.0, alias="PostTime")
    style: GjgjBeatStyle | None = Field(alias="Style")
    velocity: int | None = Field(127, alias="Velocity")


class GjgjKeyboard(BaseModel):
    key_mode: int | None = Field(1, alias="KeyMode")
    key_type: int | None = Field(0, alias="KeyType")


class GjgjTrackVolume(BaseModel):
    volume: float | None = Field(1.0, alias="Volume")
    left_volume: float | None = Field(1.0, alias="LeftVolume")
    right_volume: float | None = Field(1.0, alias="RightVolume")
    mute: bool = Field(False, alias="Mute")


class GjgjProjectSetting(BaseModel):
    no1_key_name: str | None = Field("C", alias="No1KeyName")
    eq_after_mix: str | None = Field("", alias="EQAfterMix")
    project_type: int | None = Field(0, alias="ProjectType")
    denominator: int | None = Field(4, alias="Denominator")
    syn_mode: int | None = Field(0, alias="SynMode")


class GjgjSingerInfo(BaseModel):
    name: str = Field("", alias="Name")
    display_name: str = Field("", alias="DisplayName")
    template_id: str | None = Field("", alias="TemplateID")
    sex: str | None = Field("", alias="Sex")
    age: int | None = Field(100, alias="Age")
    color: int | None = Field(0, alias="Color")
    user_id: str | None = Field("", alias="UserID")
    up_pitch: int | None = Field(0, alias="UpPitch")
    low_pitch: int | None = Field(0, alias="LowPitch")
    recommend_up_pitch: int | None = Field(0, alias="RecommandUpPitch")
    recommend_low_pitch: int | None = Field(0, alias="RecommandLowPitch")
    image: str | None = ""
    image_url: str | None = ""
    full_avatar: str | None = ""
    synthesize_file: str | None = Field("", alias="synthetize_file")


class GjgjTempos(BaseModel):
    time: int | None = Field(alias="Time")
    microseconds_per_quarter_note: int | None = Field(alias="MicrosecondsPerQuarterNote")


class GjgjTimeSignature(BaseModel):
    time: int = Field(0, alias="Time")
    numerator: int = Field(4, alias="Numerator")
    denominator: int = Field(4, alias="Denominator")


class GjgjPoint(BaseModel):
    x: float = Field(alias="X")
    y: float = Field(alias="Y")


class GjgjTone(BaseModel):
    modifies: list[GjgjPoint] = Field(default_factory=list, alias="Modifys")
    modify_ranges: list[GjgjPoint] = Field(default_factory=list, alias="ModifyRanges")


class GjgjTempoMap(BaseModel):
    ticks_per_quarter_note: int = Field(TICKS_IN_BEAT, alias="TicksPerQuarterNote")
    tempos: list[GjgjTempos] = Field(default_factory=list, alias="Tempos")
    time_signature: list[GjgjTimeSignature] = Field(default_factory=list, alias="TimeSignature")


class GjgjVolumeMap(BaseModel):
    time: int = Field(0, alias="Time")
    volume: float = Field(0.0, alias="Volume")


class GjgjSingingTrack(BaseModel):
    id_value: str | None = Field(None, alias="ID")
    type_: int | None = Field(0, alias="Type")
    name: str | None = Field(None, alias="Name")
    beat_items: list[GjgjBeatItems] = Field(default_factory=list, alias="BeatItems")
    tone: GjgjTone = Field(default_factory=GjgjTone, alias="Tone")
    volume_map: list[GjgjVolumeMap] = Field(default_factory=list, alias="VolumeMap")
    singer_info: GjgjSingerInfo = Field(default_factory=GjgjSingerInfo, alias="SingerInfo")
    keyboard: GjgjKeyboard | None = Field(default_factory=GjgjKeyboard, alias="Keyboard")
    master_volume: GjgjTrackVolume | None = Field(None, alias="MasterVolume")
    eq_program: str | None = Field("无", alias="EQProgram")
    sort_index: int | None = Field(0, alias="SortIndex")


class GjgjInstrumentalTrack(BaseModel):
    id_value: str | None = Field(None, alias="ID")
    type_: int | None = Field(1, alias="Type")
    path: str | None = Field(None, alias="Path")
    offset: int = Field(alias="Offset")
    master_volume: GjgjTrackVolume | None = Field(None, alias="MasterVolume")
    eq_program: str | None = Field("", alias="EQProgram")
    sort_index: int | None = Field(0, alias="SortIndex")


class GjgjMidiControl(BaseModel):
    control_num: int | None = Field(None, alias="ControlNum")
    volume_map: list[GjgjVolumeMap] = Field(default_factory=list, alias="VolumeMap")


class GjgjMidiTrack(BaseModel):
    id_value: str | None = Field(None, alias="ID")
    type_: int | None = Field(2, alias="Type")
    sort_index: int | None = Field(None, alias="SortIndex")
    bank: int | None = Field(None, alias="Bank")
    program: int | None = Field(None, alias="Program")
    channel: int | None = Field(None, alias="Channel")
    beat_items: list[GjgjBeatItems] = Field(default_factory=list, alias="BeatItems")
    control_map: list[GjgjMidiControl] = Field(default_factory=list, alias="ControlMap")


class GjgjProject(BaseModel):
    gjgj_version: int | None = Field(2, alias="gjgjVersion")
    project_setting: GjgjProjectSetting | None = Field(
        default_factory=GjgjProjectSetting, alias="ProjectSetting"
    )
    accompaniments: list[GjgjInstrumentalTrack] = Field(
        default_factory=list, alias="Accompaniments"
    )
    tracks: list[GjgjSingingTrack] = Field(default_factory=list, alias="Tracks")
    midi_tracks: list[GjgjMidiTrack] = Field(default_factory=list, alias="MIDITracks")
    tempo_map: GjgjTempoMap = Field(default_factory=GjgjTempoMap, alias="TempoMap")
