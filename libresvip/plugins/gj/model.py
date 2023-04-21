from enum import Enum
from typing import List, Optional

from pydantic import Field

from libresvip.model.base import BaseModel


class GjgjBeatStyle(Enum):
    NONE = 0
    SP = 1
    SIL = 2


class GjgjBeatItems(BaseModel):
    id: Optional[int] = Field(alias="ID")
    lyric: Optional[str] = Field(alias="Lyric")
    pinyin: Optional[str] = Field(alias="Pinyin")
    start_tick: Optional[int] = Field(alias="StartTick")
    duration: Optional[int] = Field(alias="Duration")
    track: Optional[int] = Field(alias="Track")
    pre_time: Optional[float] = Field(alias="PreTime")
    post_time: Optional[float] = Field(alias="PostTime")
    style: Optional[GjgjBeatStyle] = Field(alias="Style")
    velocity: Optional[int] = Field(127, alias="Velocity")


class GjgjKeyboard(BaseModel):
    key_mode: Optional[int] = Field(1, alias="KeyMode")
    key_type: Optional[int] = Field(0, alias="KeyType")


class GjgjTrackVolume(BaseModel):
    volume: Optional[float] = Field(1.0, alias="Volume")
    left_volume: Optional[float] = Field(1.0, alias="LeftVolume")
    right_volume: Optional[float] = Field(1.0, alias="RightVolume")
    mute: Optional[bool] = Field(alias="Mute")


class GjgjProjectSetting(BaseModel):
    no1_key_name: Optional[str] = Field("C", alias="No1KeyName")
    eq_after_mix: Optional[str] = Field("", alias="EQAfterMix")
    project_type: Optional[int] = Field(0, alias="ProjectType")
    denominator: Optional[int] = Field(4, alias="Denominator")
    syn_mode: Optional[int] = Field(0, alias="SynMode")


class GjgjSingerInfo(BaseModel):
    name: Optional[str] = Field("", alias="Name")
    display_name: Optional[str] = Field("", alias="DisplayName")
    template_id: Optional[str] = Field("", alias="TemplateID")
    sex: Optional[str] = Field("", alias="Sex")
    age: Optional[int] = Field(100, alias="Age")
    color: Optional[int] = Field(0, alias="Color")
    user_id: Optional[str] = Field('', alias="UserID")
    up_pitch: Optional[int] = Field(0, alias="UpPitch")
    low_pitch: Optional[int] = Field(0, alias="LowPitch")
    recommend_up_pitch: Optional[int] = Field(0, alias="RecommandUpPitch")
    recommend_low_pitch: Optional[int] = Field(0, alias="RecommandLowPitch")
    image: Optional[str] = ''
    image_url: Optional[str] = ''
    full_avatar: Optional[str] = ''
    synthesize_file: Optional[str] = Field('', alias="synthetize_file")


class GjgjTempos(BaseModel):
    time: Optional[int] = Field(alias="Time")
    microseconds_per_quarter_note: Optional[int] = Field(
        alias="MicrosecondsPerQuarterNote"
    )


class GjgjTimeSignature(BaseModel):
    time: Optional[int] = Field(alias="Time")
    numerator: Optional[int] = Field(alias="Numerator")
    denominator: Optional[int] = Field(alias="Denominator")


class GjgjPoint(BaseModel):
    x: Optional[float] = Field(alias="X")
    y: Optional[float] = Field(alias="Y")


class GjgjTone(BaseModel):
    modifies: List[GjgjPoint] = Field(default_factory=list, alias="Modifys")
    modify_ranges: List[GjgjPoint] = Field(default_factory=list, alias="ModifyRanges")


class GjgjTempoMap(BaseModel):
    ticks_per_quarter_note: Optional[int] = Field(alias="TicksPerQuarterNote")
    tempos: List[GjgjTempos] = Field(default_factory=list, alias="Tempos")
    time_signature: List[GjgjTimeSignature] = Field(
        default_factory=list, alias="TimeSignature"
    )


class GjgjVolumeMap(BaseModel):
    time: Optional[int] = Field(alias="Time")
    volume: Optional[float] = Field(alias="Volume")


class GjgjSingingTrack(BaseModel):
    id: Optional[str] = Field(alias="ID")
    type_: Optional[int] = Field(0, alias="Type")
    name: Optional[str] = Field(alias="Name")
    beat_items: List[GjgjBeatItems] = Field(default_factory=list, alias="BeatItems")
    tone: Optional[GjgjTone] = Field(default_factory=GjgjTone, alias="Tone")
    volume_map: List[GjgjVolumeMap] = Field(default_factory=list, alias="VolumeMap")
    singer_info: Optional[GjgjSingerInfo] = Field(
        default_factory=GjgjSingerInfo, alias="SingerInfo"
    )
    keyboard: Optional[GjgjKeyboard] = Field(
        default_factory=GjgjKeyboard, alias="Keyboard"
    )
    master_volume: Optional[GjgjTrackVolume] = Field(alias="MasterVolume")
    eq_program: Optional[str] = Field("无", alias="EQProgram")
    sort_index: Optional[int] = Field(0, alias="SortIndex")


class GjgjInstrumentalTrack(BaseModel):
    id: Optional[str] = Field(alias="ID")
    type_: Optional[int] = Field(1, alias="Type")
    path: Optional[str] = Field(alias="Path")
    offset: Optional[int] = Field(alias="Offset")
    master_volume: Optional[GjgjTrackVolume] = Field(alias="MasterVolume")
    eq_program: Optional[str] = Field("", alias="EQProgram")
    sort_index: Optional[int] = Field(0, alias="SortIndex")


class GjgjMidiControl(BaseModel):
    control_num: Optional[int] = Field(alias="ControlNum")
    volume_map: List[GjgjVolumeMap] = Field(default_factory=list, alias="VolumeMap")


class GjgjMidiTrack(BaseModel):
    id: Optional[str] = Field(alias="ID")
    type_: Optional[int] = Field(2, alias="Type")
    sort_index: Optional[int] = Field(alias="SortIndex")
    bank: Optional[int] = Field(alias="Bank")
    program: Optional[int] = Field(alias="Program")
    channel: Optional[int] = Field(alias="Channel")
    beat_items: List[GjgjBeatItems] = Field(default_factory=list, alias="BeatItems")
    control_map: List[GjgjMidiControl] = Field(default_factory=list, alias="ControlMap")


class GjgjProject(BaseModel):

    gjgj_version: Optional[int] = Field(alias="gjgjVersion")
    project_setting: Optional[GjgjProjectSetting] = Field(
        default_factory=GjgjProjectSetting, alias="ProjectSetting"
    )
    accompaniments: List[GjgjInstrumentalTrack] = Field(
        default_factory=list, alias="Accompaniments"
    )
    tracks: List[GjgjSingingTrack] = Field(default_factory=list, alias="Tracks")
    midi_tracks: List[GjgjMidiTrack] = Field(default_factory=list, alias="MIDITracks")
    tempo_map: Optional[GjgjTempoMap] = Field(alias="TempoMap")
