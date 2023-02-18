from typing import List, Optional, Union

from pydantic import Field

from libresvip.model.base import BaseModel


class VocaloidEvents(BaseModel):
    bar: Optional[int]
    denom: Optional[int]
    numer: Optional[int]
    pos: Optional[int]
    value: Optional[int]


class VocaloidExp(BaseModel):
    opening: Optional[int]


class VocaloidGlobal(BaseModel):
    is_enabled: Optional[bool] = Field(alias="isEnabled")
    value: Optional[int]


class VocaloidLoop(BaseModel):
    begin: Optional[int]
    end: Optional[int]
    is_enabled: Optional[bool] = Field(alias="isEnabled")


class VocaloidParameters(BaseModel):
    name: Optional[str]
    value: Optional[Union[int, str]]


class VocaloidVersion(BaseModel):
    major: Optional[int]
    minor: Optional[int]
    revision: Optional[int]


class VocaloidVibrato(BaseModel):
    type: Optional[int]
    duration: Optional[int]


class VocaloidVoice(BaseModel):
    comp_id: Optional[str] = Field(alias="compID")
    lang_id: Optional[int] = Field(alias="langID")


class VocaloidVoices(BaseModel):
    comp_id: Optional[str] = Field(alias="compID")
    name: Optional[str]


class VocaloidWeight(BaseModel):
    pre: Optional[int]
    post: Optional[int]


class VocaloidControllers(BaseModel):
    name: Optional[str]
    events: List[VocaloidEvents] = Field(default_factory=list)


class VocaloidMidiEffects(BaseModel):
    id: Optional[str]
    is_bypassed: Optional[bool] = Field(alias="isBypassed")
    is_folded: Optional[bool] = Field(alias="isFolded")
    parameters: List[VocaloidParameters] = Field(default_factory=list)


class VocaloidPanpot(BaseModel):
    is_folded: Optional[bool] = Field(alias="isFolded")
    height: Optional[int]
    events: List[VocaloidEvents] = Field(default_factory=list)


class VocaloidSingingSkill(BaseModel):
    duration: Optional[int]
    weight: Optional[VocaloidWeight]


class VocaloidTempo(BaseModel):
    events: List[VocaloidEvents] = Field(default_factory=list)
    global_value: Optional[VocaloidGlobal] = Field(alias="global")
    height: Optional[int]
    is_folded: Optional[bool] = Field(alias="isFolded")


class VocaloidTimeSig(BaseModel):
    events: List[VocaloidEvents] = Field(default_factory=list)
    is_folded: Optional[bool] = Field(alias="isFolded")


class VocaloidVolume(BaseModel):
    is_folded: Optional[bool] = Field(alias="isFolded")
    height: Optional[int]
    events: List[VocaloidEvents] = Field(default_factory=list)


class VocaloidMasterTrack(BaseModel):
    loop: Optional[VocaloidLoop]
    sampling_rate: Optional[int] = Field(alias="samplingRate")
    tempo: Optional[VocaloidTempo]
    time_sig: Optional[VocaloidTimeSig] = Field(alias="timeSig")
    volume: Optional[VocaloidVolume]


class VocaloidNotes(BaseModel):
    duration: Optional[int]
    exp: Optional[VocaloidExp]
    is_protected: Optional[bool] = Field(alias="isProtected")
    lyric: Optional[str]
    number: Optional[int]
    phoneme: Optional[str]
    pos: Optional[int]
    singing_skill: Optional[VocaloidSingingSkill] = Field(alias="singingSkill")
    velocity: Optional[int]
    vibrato: Optional[VocaloidVibrato]


class VocaloidParts(BaseModel):
    duration: Optional[int]
    midi_effects: List[VocaloidMidiEffects] = Field(
        default_factory=list, alias="midiEffects"
    )
    notes: List[VocaloidNotes]
    pos: Optional[int]
    style_name: Optional[str]
    voice: Optional[VocaloidVoice]
    controllers: List[VocaloidControllers] = Field(default_factory=list)


class VocaloidTracks(BaseModel):
    bus_no: Optional[int] = Field(alias="busNo")
    color: Optional[int]
    height: Optional[int]
    is_folded: Optional[bool] = Field(alias="isFolded")
    is_muted: Optional[bool] = Field(alias="isMuted")
    is_solo_mode: Optional[bool] = Field(alias="isSoloMode")
    name: Optional[str]
    panpot: Optional[VocaloidPanpot]
    parts: List[VocaloidParts] = Field(default_factory=list)
    type: Optional[int]
    volume: Optional[VocaloidVolume]


class VocaloidProject(BaseModel):
    master_track: Optional[VocaloidMasterTrack] = Field(alias="masterTrack")
    title: Optional[str]
    tracks: List[VocaloidTracks] = Field(default_factory=list)
    vender: Optional[str]
    version: Optional[VocaloidVersion]
    voices: List[VocaloidVoices] = Field(default_factory=list)
