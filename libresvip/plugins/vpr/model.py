from typing import Optional, Union

from pydantic import Extra, Field

from libresvip.model.base import BaseModel


class VocaloidPoint(BaseModel):
    pos: Optional[int]
    value: Optional[int]


class VocaloidEvents(VocaloidPoint):
    bar: Optional[int]
    denom: Optional[int]
    numer: Optional[int]


class VocaloidExp(BaseModel):
    opening: Optional[int]
    accent: Optional[int]
    decay: Optional[int]
    bend_depth: Optional[int] = Field(alias="bendDepth")
    bend_length: Optional[int] = Field(alias="bendLength")


class VocaloidAIExp(BaseModel):
    pitch_fine: Optional[float] = Field(alias="pitchFine")
    pitch_drift_start: Optional[float] = Field(alias="pitchDriftStart")
    pitch_drift_end: Optional[float] = Field(alias="pitchDriftEnd")
    pitch_scaling_center: Optional[float] = Field(alias="pitchScalingCenter")
    pitch_scaling_origin: Optional[float] = Field(alias="pitchScalingOrigin")
    pitch_transition_start: Optional[float] = Field(alias="pitchTransitionStart")
    pitch_transition_end: Optional[float] = Field(alias="pitchTransitionEnd")
    amplitude_whole: Optional[float] = Field(alias="amplitudeWhole")
    amplitude_start: Optional[float] = Field(alias="amplitudeStart")
    amplitude_end: Optional[float] = Field(alias="amplitudeEnd")
    formant_whole: Optional[float] = Field(alias="formantWhole")
    formant_start: Optional[float] = Field(alias="formantStart")
    formant_end: Optional[float] = Field(alias="formantEnd")


class VocaloidEnabled(BaseModel):
    is_enabled: Optional[bool] = Field(alias="isEnabled")


class VocaloidGlobal(VocaloidEnabled):
    value: Optional[int]


class VocaloidRegion(VocaloidEnabled):
    begin: Optional[int]
    end: Optional[int]


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
    depths: Optional[list[VocaloidPoint]] = Field(default_factory=list)
    rates: Optional[list[VocaloidPoint]] = Field(default_factory=list)


class VocaloidCompID(BaseModel):
    comp_id: Optional[str] = Field(alias="compID")


class VocaloidLangID(BaseModel):
    lang_id: Optional[int] = Field(alias="langID")


class VocaloidVoice(VocaloidCompID, VocaloidLangID):
    pass


class VocaloidAIVoice(VocaloidCompID):
    lang_ids: list[VocaloidLangID] = Field(default_factory=list, alias="langIDs")


class VocaloidVoices(VocaloidCompID):
    name: Optional[str]


class VocaloidWeight(BaseModel):
    pre: Optional[int]
    post: Optional[int]


class VocaloidControllers(BaseModel):
    name: Optional[str]
    events: list[VocaloidEvents] = Field(default_factory=list)


class VocaloidMidiEffects(BaseModel):
    id: Optional[str]
    is_bypassed: Optional[bool] = Field(alias="isBypassed")
    is_folded: Optional[bool] = Field(alias="isFolded")
    parameters: list[VocaloidParameters] = Field(default_factory=list)


class VocaloidPanpot(BaseModel):
    is_folded: Optional[bool] = Field(alias="isFolded")
    height: Optional[int]
    events: list[VocaloidEvents] = Field(default_factory=list)


class VocaloidSingingSkill(BaseModel):
    duration: Optional[int]
    weight: Optional[VocaloidWeight]


class VocaloidTempo(BaseModel):
    events: list[VocaloidEvents] = Field(default_factory=list)
    global_value: Optional[VocaloidGlobal] = Field(alias="global")
    height: Optional[int]
    is_folded: Optional[bool] = Field(alias="isFolded")
    ara: Optional[VocaloidEnabled]


class VocaloidTimeSig(BaseModel):
    events: list[VocaloidEvents] = Field(default_factory=list)
    is_folded: Optional[bool] = Field(alias="isFolded")


class VocaloidVolume(BaseModel):
    is_folded: Optional[bool] = Field(alias="isFolded")
    height: Optional[int]
    events: list[VocaloidEvents] = Field(default_factory=list)


class VocaloidMasterTrack(BaseModel):
    loop: Optional[VocaloidRegion]
    sampling_rate: Optional[int] = Field(alias="samplingRate")
    tempo: Optional[VocaloidTempo]
    time_sig: Optional[VocaloidTimeSig] = Field(alias="timeSig")
    volume: Optional[VocaloidVolume]


class VocaloidNotes(VocaloidLangID):
    duration: Optional[int]
    exp: Optional[VocaloidExp]
    ai_exp: Optional[VocaloidAIExp] = Field(alias="aiExp")
    is_protected: Optional[bool] = Field(alias="isProtected")
    lyric: Optional[str]
    number: Optional[int]
    phoneme: Optional[str]
    pos: Optional[int]
    singing_skill: Optional[VocaloidSingingSkill] = Field(alias="singingSkill")
    velocity: Optional[int]
    vibrato: Optional[VocaloidVibrato]


class VocaloidWav(BaseModel):
    name: Optional[str]
    original_name: Optional[str] = Field(alias="originalName")


class VocaloidBasePart(BaseModel):
    pos: int


class VocaloidVoicePart(VocaloidBasePart, extra=Extra.forbid):
    duration: Optional[int]
    midi_effects: list[VocaloidMidiEffects] = Field(
        default_factory=list, alias="midiEffects"
    )
    notes: Optional[list[VocaloidNotes]]
    duration: Optional[int]
    style_preset_id: Optional[str] = Field(alias="stylePresetID")
    style_name: Optional[str] = Field(alias="styleName")
    voice: Optional[VocaloidVoice]
    ai_voice: Optional[VocaloidAIVoice] = Field(alias="aiVoice")
    controllers: list[VocaloidControllers] = Field(default_factory=list)


class VocaloidWavPart(VocaloidBasePart):
    region: Optional[VocaloidRegion]
    name: Optional[str]
    wav: Optional[VocaloidWav]


VocaloidParts = Union[VocaloidVoicePart, VocaloidWavPart]


class VocaloidTracks(BaseModel):
    bus_no: Optional[int] = Field(alias="busNo")
    color: Optional[int]
    height: Optional[int]
    is_folded: Optional[bool] = Field(alias="isFolded")
    is_muted: Optional[bool] = Field(alias="isMuted")
    is_solo_mode: Optional[bool] = Field(alias="isSoloMode")
    name: Optional[str]
    panpot: Optional[VocaloidPanpot]
    parts: list[VocaloidParts] = Field(default_factory=list)
    type: Optional[int]
    volume: Optional[VocaloidVolume]
    last_scroll_position_note_number: Optional[int] = Field(
        alias="lastScrollPositionNoteNumber"
    )


class VocaloidProject(BaseModel):
    master_track: Optional[VocaloidMasterTrack] = Field(alias="masterTrack")
    title: Optional[str]
    tracks: list[VocaloidTracks] = Field(default_factory=list)
    vender: Optional[str]
    version: Optional[VocaloidVersion]
    voices: list[VocaloidVoices] = Field(default_factory=list)
