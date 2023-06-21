from typing import Optional, Union

from pydantic import Extra, Field

from libresvip.model.base import BaseModel


class VocaloidBasePos(BaseModel):
    pos: int


class VocaloidWithDur(VocaloidBasePos):
    duration: Optional[int] = None


class VocaloidPoint(VocaloidBasePos):
    value: Optional[int] = None


class VocaloidTimeSig(BaseModel):
    bar: Optional[int] = None
    denom: Optional[int] = None
    numer: Optional[int] = None


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
    value: Optional[int] = None


class VocaloidRegion(VocaloidEnabled):
    begin: Optional[float] = None
    end: Optional[float] = None


class VocaloidParameters(BaseModel):
    name: Optional[str] = None
    value: Optional[Union[int, str]] = None


class VocaloidVersion(BaseModel):
    major: Optional[int] = None
    minor: Optional[int] = None
    revision: Optional[int] = None


class VocaloidVibrato(BaseModel):
    type: Optional[int] = None
    duration: Optional[int] = None
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
    name: Optional[str] = None


class VocaloidWeight(BaseModel):
    pre: Optional[int] = None
    post: Optional[int] = None


class VocaloidControllers(BaseModel):
    name: Optional[str] = None
    events: list[VocaloidPoint] = Field(default_factory=list)


class VocaloidMidiEffects(BaseModel):
    id: Optional[str] = None
    is_bypassed: Optional[bool] = Field(alias="isBypassed")
    is_folded: Optional[bool] = Field(alias="isFolded")
    parameters: list[VocaloidParameters] = Field(default_factory=list)


class VocaloidSingingSkill(BaseModel):
    duration: Optional[int] = None
    weight: Optional[VocaloidWeight] = None


class VocaloidTempo(BaseModel):
    events: list[VocaloidPoint] = Field(default_factory=list)
    global_value: Optional[VocaloidGlobal] = Field(alias="global")
    height: Optional[int] = None
    is_folded: Optional[bool] = Field(alias="isFolded")
    ara: Optional[VocaloidEnabled] = None


class VocaloidTimeSigs(BaseModel):
    events: list[VocaloidTimeSig] = Field(default_factory=list)
    is_folded: Optional[bool] = Field(alias="isFolded")


class VocaloidAutomation(BaseModel):
    is_folded: Optional[bool] = Field(alias="isFolded")
    height: Optional[int] = None
    events: list[VocaloidPoint] = Field(default_factory=list)


class VocaloidMasterTrack(BaseModel):
    loop: Optional[VocaloidRegion] = None
    sampling_rate: Optional[int] = Field(alias="samplingRate")
    tempo: Optional[VocaloidTempo] = None
    time_sig: Optional[VocaloidTimeSigs] = Field(alias="timeSig")
    volume: Optional[VocaloidAutomation] = None


class VocaloidDVQMRelease(VocaloidCompID):
    speed: Optional[int] = None
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
    lyric: Optional[str] = None
    number: Optional[int] = None
    phoneme: Optional[str] = None
    phoneme_positions: list[VocaloidBasePos] = Field(
        default_factory=list, alias="phonemePositions"
    )
    singing_skill: Optional[VocaloidSingingSkill] = Field(None, alias="singingSkill")
    velocity: Optional[int] = None
    vibrato: Optional[VocaloidVibrato] = None
    dvqm: Optional[VocaloidDVQM] = None


class VocaloidWav(BaseModel):
    name: Optional[str] = None
    original_name: Optional[str] = Field(alias="originalName")


class VocaloidVoicePart(VocaloidWithDur, extra=Extra.forbid):
    name: Optional[str] = None
    midi_effects: list[VocaloidMidiEffects] = Field(
        default_factory=list, alias="midiEffects"
    )
    notes: Optional[list[VocaloidNotes]] = None
    style_preset_id: Optional[str] = Field(None, alias="stylePresetID")
    style_name: Optional[str] = Field(None, alias="styleName")
    voice: Optional[VocaloidVoice] = None
    ai_voice: Optional[VocaloidAIVoice] = Field(None, alias="aiVoice")
    controllers: list[VocaloidControllers] = Field(default_factory=list)


class VocaloidWavPart(VocaloidBasePos):
    region: Optional[VocaloidRegion] = None
    name: Optional[str] = None
    wav: Optional[VocaloidWav] = None


VocaloidParts = Union[VocaloidVoicePart, VocaloidWavPart]


class VocaloidTracks(BaseModel):
    bus_no: Optional[int] = Field(alias="busNo")
    color: Optional[int] = None
    height: Optional[int] = None
    is_folded: Optional[bool] = Field(alias="isFolded")
    is_muted: Optional[bool] = Field(alias="isMuted")
    is_solo_mode: Optional[bool] = Field(alias="isSoloMode")
    name: Optional[str] = None
    panpot: Optional[VocaloidAutomation] = None
    parts: list[VocaloidParts] = Field(default_factory=list)
    type: Optional[int] = None
    volume: Optional[VocaloidAutomation] = None
    last_scroll_position_note_number: Optional[int] = Field(
        None, alias="lastScrollPositionNoteNumber"
    )


class VocaloidProject(BaseModel):
    master_track: Optional[VocaloidMasterTrack] = Field(alias="masterTrack")
    title: Optional[str] = None
    tracks: list[VocaloidTracks] = Field(default_factory=list)
    vender: Optional[str] = None
    version: Optional[VocaloidVersion] = None
    voices: list[VocaloidVoices] = Field(default_factory=list)
