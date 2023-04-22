from typing import Optional, Union

from pydantic import Extra, Field

from libresvip.model.base import BaseModel


class VocaloidBasePos(BaseModel):
    pos: int


class VocaloidWithDur(VocaloidBasePos):
    duration: Optional[int]


class VocaloidPoint(VocaloidBasePos):
    value: Optional[int]


class VocaloidTimeSig(BaseModel):
    bar: Optional[int]
    denom: Optional[int]
    numer: Optional[int]


class VocaloidExp(BaseModel):
    opening: Optional[int] = None
    accent: Optional[int] = None
    decay: Optional[int] = None
    bend_depth: Optional[int] = Field(None, alias="bendDepth")
    bend_length: Optional[int] = Field(None, alias="bendLength")


class VocaloidAIExp(BaseModel):
    pitch_fine: Optional[float] = Field(None, alias="pitchFine")
    pitch_drift_start: Optional[float] = Field(None, alias="pitchDriftStart")
    pitch_drift_end: Optional[float] = Field(None, alias="pitchDriftEnd")
    pitch_scaling_center: Optional[float] = Field(None, alias="pitchScalingCenter")
    pitch_scaling_origin: Optional[float] = Field(None, alias="pitchScalingOrigin")
    pitch_transition_start: Optional[float] = Field(None, alias="pitchTransitionStart")
    pitch_transition_end: Optional[float] = Field(None, alias="pitchTransitionEnd")
    amplitude_whole: Optional[float] = Field(None, alias="amplitudeWhole")
    amplitude_start: Optional[float] = Field(None, alias="amplitudeStart")
    amplitude_end: Optional[float] = Field(None, alias="amplitudeEnd")
    formant_whole: Optional[float] = Field(None, alias="formantWhole")
    formant_start: Optional[float] = Field(None, alias="formantStart")
    formant_end: Optional[float] = Field(None, alias="formantEnd")


class VocaloidEnabled(BaseModel):
    is_enabled: Optional[bool] = Field(None, alias="isEnabled")


class VocaloidGlobal(VocaloidEnabled):
    value: Optional[int]


class VocaloidRegion(VocaloidEnabled):
    begin: Optional[float]
    end: Optional[float]


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
    lang_id: Optional[int] = Field(None, alias="langID")


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
    events: list[VocaloidPoint] = Field(default_factory=list)


class VocaloidMidiEffects(BaseModel):
    id: Optional[str]
    is_bypassed: Optional[bool] = Field(alias="isBypassed")
    is_folded: Optional[bool] = Field(alias="isFolded")
    parameters: list[VocaloidParameters] = Field(default_factory=list)


class VocaloidSingingSkill(BaseModel):
    duration: Optional[int]
    weight: Optional[VocaloidWeight]


class VocaloidTempo(BaseModel):
    events: list[VocaloidPoint] = Field(default_factory=list)
    global_value: Optional[VocaloidGlobal] = Field(alias="global")
    height: Optional[int]
    is_folded: Optional[bool] = Field(alias="isFolded")
    ara: Optional[VocaloidEnabled] = None


class VocaloidTimeSigs(BaseModel):
    events: list[VocaloidTimeSig] = Field(default_factory=list)
    is_folded: Optional[bool] = Field(alias="isFolded")


class VocaloidAutomation(BaseModel):
    is_folded: Optional[bool] = Field(alias="isFolded")
    height: Optional[int]
    events: list[VocaloidPoint] = Field(default_factory=list)


class VocaloidMasterTrack(BaseModel):
    loop: Optional[VocaloidRegion]
    sampling_rate: Optional[int] = Field(alias="samplingRate")
    tempo: Optional[VocaloidTempo]
    time_sig: Optional[VocaloidTimeSigs] = Field(alias="timeSig")
    volume: Optional[VocaloidAutomation]


class VocaloidDVQMRelease(VocaloidCompID):
    speed: Optional[int]
    level_names: Optional[list[str]] = Field(alias="levelNames")
    top_factor: Optional[float] = Field(alias="topFactor")
    is_protected: Optional[bool] = Field(alias="isProtected")


class VocaloidDVQM(BaseModel):
    release: Optional[VocaloidDVQMRelease] = None
    attack: Optional[VocaloidDVQMRelease] = None


class VocaloidNotes(VocaloidLangID, VocaloidWithDur):
    exp: Optional[VocaloidExp] = None
    ai_exp: Optional[VocaloidAIExp] = Field(None, alias="aiExp")
    is_protected: Optional[bool] = Field(alias="isProtected")
    lyric: Optional[str]
    number: Optional[int]
    phoneme: Optional[str]
    phoneme_positions: list[VocaloidBasePos] = Field(
        default_factory=list, alias="phonemePositions"
    )
    singing_skill: Optional[VocaloidSingingSkill] = Field(None, alias="singingSkill")
    velocity: Optional[int]
    vibrato: Optional[VocaloidVibrato]
    dvqm: Optional[VocaloidDVQM] = None


class VocaloidWav(BaseModel):
    name: Optional[str]
    original_name: Optional[str] = Field(alias="originalName")


class VocaloidVoicePart(VocaloidWithDur, extra=Extra.forbid):
    name: Optional[str] = None
    midi_effects: list[VocaloidMidiEffects] = Field(
        default_factory=list, alias="midiEffects"
    )
    notes: Optional[list[VocaloidNotes]]
    style_preset_id: Optional[str] = Field(None, alias="stylePresetID")
    style_name: Optional[str] = Field(None, alias="styleName")
    voice: Optional[VocaloidVoice] = None
    ai_voice: Optional[VocaloidAIVoice] = Field(None, alias="aiVoice")
    controllers: list[VocaloidControllers] = Field(default_factory=list)


class VocaloidWavPart(VocaloidBasePos):
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
    panpot: Optional[VocaloidAutomation]
    parts: list[VocaloidParts] = Field(default_factory=list)
    type: Optional[int]
    volume: Optional[VocaloidAutomation]
    last_scroll_position_note_number: Optional[int] = Field(
        None, alias="lastScrollPositionNoteNumber"
    )


class VocaloidProject(BaseModel):
    master_track: Optional[VocaloidMasterTrack] = Field(alias="masterTrack")
    title: Optional[str]
    tracks: list[VocaloidTracks] = Field(default_factory=list)
    vender: Optional[str]
    version: Optional[VocaloidVersion]
    voices: list[VocaloidVoices] = Field(default_factory=list)
