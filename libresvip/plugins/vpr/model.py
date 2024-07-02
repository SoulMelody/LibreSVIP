import enum
from dataclasses import dataclass
from typing import Annotated, Literal, Optional, Union

from pydantic import ConfigDict, Field

from libresvip.model.base import BaseModel
from libresvip.utils.translation import gettext_lazy as _


class VocaloidLanguage(enum.IntEnum):
    JAPANESE: Annotated[int, Field(title=_("日本語"))] = 0
    ENGLISH: Annotated[int, Field(title=_("English"))] = 1
    KOREAN: Annotated[int, Field(title=_("한국어"))] = 2
    SPANISH: Annotated[int, Field(title=_("Español"))] = 3
    SIMPLIFIED_CHINESE: Annotated[int, Field(title=_("简体中文"))] = 4


class VocaloidTrackType(enum.IntEnum):
    STANDARD = 0
    AUDIO = 1
    AI = 2


@dataclass
class ControllerEvent:
    pos: int
    value: int


@dataclass
class VocaloidPartPitchData:
    start_pos: int
    pit: list[ControllerEvent]
    pbs: list[ControllerEvent]


class VocaloidBasePos(BaseModel):
    pos: int = 0


class VocaloidWithDur(VocaloidBasePos):
    duration: Optional[int] = None


class VocaloidPoint(VocaloidBasePos):
    value: Optional[Union[int, float]] = None


class VocaloidTimeSig(BaseModel):
    bar: int = 0
    denom: int = 4
    numer: int = 4


class VocaloidExp(BaseModel):
    opening: Optional[int] = 127
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
    is_enabled: Optional[bool] = Field(True, alias="isEnabled")


class VocaloidGlobal(VocaloidEnabled):
    value: Optional[int] = 12000


class VocaloidRegion(VocaloidEnabled):
    begin: Optional[float] = 0
    end: Optional[float] = 7680


class VocaloidParameters(BaseModel):
    name: Optional[str] = None
    value: Optional[Union[int, float, str]] = None


class VocaloidVersion(BaseModel):
    major: int = 5
    minor: int = 0
    revision: int = 0


class VocaloidVibrato(BaseModel):
    type_value: Optional[int] = Field(0, alias="type")
    duration: Optional[int] = 0
    depths: Optional[list[VocaloidPoint]] = Field(default_factory=list)
    rates: Optional[list[VocaloidPoint]] = Field(default_factory=list)


class VocaloidCompID(BaseModel):
    comp_id: Optional[str] = Field(None, alias="compID")


class VocaloidLangID(BaseModel):
    lang_id: Optional[VocaloidLanguage] = Field(VocaloidLanguage.SIMPLIFIED_CHINESE, alias="langID")


class VocaloidVoice(VocaloidCompID, VocaloidLangID):
    pass


class VocaloidAIVoice(VocaloidCompID):
    lang_ids: list[VocaloidLangID] = Field(default_factory=list, alias="langIDs")


class VocaloidVoices(VocaloidCompID):
    name: Optional[str] = None


class VocaloidWeight(BaseModel):
    pre: Optional[int] = 64
    post: Optional[int] = 64


class VocaloidControllers(BaseModel):
    name: Optional[str] = None
    events: list[VocaloidPoint] = Field(default_factory=list)


class VocaloidFolded(BaseModel):
    is_folded: Optional[bool] = Field(True, alias="isFolded")


class VocaloidEffects(VocaloidFolded):
    id_value: Optional[str] = Field(None, alias="id")
    is_bypassed: Optional[bool] = Field(None, alias="isBypassed")
    parameters: list[VocaloidParameters] = Field(default_factory=list)


class VocaloidSingingSkill(BaseModel):
    duration: Optional[int] = 158
    weight: Optional[VocaloidWeight] = Field(default_factory=VocaloidWeight)


class VocaloidTempo(VocaloidFolded):
    events: list[VocaloidPoint] = Field(default_factory=list)
    global_value: Optional[VocaloidGlobal] = Field(alias="global", default_factory=VocaloidGlobal)
    height: Optional[int] = 0
    ara: Optional[VocaloidEnabled] = None


class VocaloidTimeSigs(VocaloidFolded):
    events: list[VocaloidTimeSig] = Field(default_factory=list)


class VocaloidAutomation(VocaloidFolded):
    height: int = 0
    events: list[VocaloidPoint] = Field(default_factory=list)


class VocaloidMasterTrack(BaseModel):
    loop: VocaloidRegion = Field(default_factory=VocaloidRegion)
    sampling_rate: int = Field(44100, alias="samplingRate")
    tempo: VocaloidTempo = Field(default_factory=VocaloidTempo)
    time_sig: VocaloidTimeSigs = Field(alias="timeSig", default_factory=VocaloidTimeSigs)
    volume: VocaloidAutomation = Field(default_factory=VocaloidAutomation)


class VocaloidDVQMRelease(VocaloidCompID):
    speed: Optional[int] = None
    level_names: Optional[list[str]] = Field(None, alias="levelNames")
    top_factor: Optional[float] = Field(None, alias="topFactor")
    is_protected: Optional[bool] = Field(None, alias="isProtected")


class VocaloidDVQM(BaseModel):
    release: Optional[VocaloidDVQMRelease] = None
    attack: Optional[VocaloidDVQMRelease] = None


class VocaloidNotes(VocaloidLangID, VocaloidWithDur):
    exp: Optional[VocaloidExp] = Field(default_factory=VocaloidExp)
    ai_exp: Optional[VocaloidAIExp] = Field(None, alias="aiExp")
    is_protected: Optional[bool] = Field(False, alias="isProtected")
    lyric: str
    number: int
    phoneme: Optional[str] = None
    phoneme_positions: Optional[list[VocaloidBasePos]] = Field(None, alias="phonemePositions")
    singing_skill: Optional[VocaloidSingingSkill] = Field(
        alias="singingSkill", default_factory=VocaloidSingingSkill
    )
    velocity: int = 64
    vibrato: Optional[VocaloidVibrato] = Field(default_factory=VocaloidVibrato)
    dvqm: Optional[VocaloidDVQM] = None


class VocaloidWav(BaseModel):
    name: str
    original_name: Optional[str] = Field(None, alias="originalName")


class VocaloidVoicePart(VocaloidWithDur):
    name: Optional[str] = ""
    midi_effects: list[VocaloidEffects] = Field(default_factory=list, alias="midiEffects")
    audio_effects: list[VocaloidEffects] = Field(default_factory=list, alias="audioEffects")
    notes: list[VocaloidNotes] = Field(default_factory=list)
    style_preset_id: Optional[str] = Field(None, alias="stylePresetID")
    style_name: Optional[str] = Field("No Effect", alias="styleName")
    voice: Optional[VocaloidVoice] = None
    ai_voice: Optional[VocaloidAIVoice] = Field(None, alias="aiVoice")
    controllers: Optional[list[VocaloidControllers]] = None

    def get_controller_events(self, name: str) -> list[ControllerEvent]:
        if self.controllers is None:
            return []
        return [
            ControllerEvent(
                pos=event.pos,
                value=int(event.value),
            )
            for controller in self.controllers
            if controller.name == name
            for event in controller.events
            if event.value is not None
        ]


class VocaloidWavPart(VocaloidBasePos):
    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid",
    )
    region: Optional[VocaloidRegion] = None
    name: Optional[str] = ""
    wav: Optional[VocaloidWav] = None


class VocaloidBaseTracks(VocaloidFolded):
    bus_no: Optional[int] = Field(0, alias="busNo")
    color: Optional[int] = 0
    height: Optional[float] = 0
    is_muted: bool = Field(False, alias="isMuted")
    is_solo_mode: bool = Field(False, alias="isSoloMode")
    name: Optional[str] = ""
    panpot: VocaloidAutomation = Field(default_factory=VocaloidAutomation)
    volume: VocaloidAutomation = Field(default_factory=VocaloidAutomation)
    last_scroll_position_note_number: Optional[int] = Field(
        None, alias="lastScrollPositionNoteNumber"
    )


class VocaloidStandardTrack(VocaloidBaseTracks):
    parts: list[VocaloidVoicePart] = Field(default_factory=list)
    type_value: Literal[VocaloidTrackType.STANDARD] = Field(
        VocaloidTrackType.STANDARD, alias="type"
    )


class VocaloidAITrack(VocaloidBaseTracks):
    parts: list[VocaloidVoicePart] = Field(default_factory=list)
    type_value: Literal[VocaloidTrackType.AI] = Field(VocaloidTrackType.AI, alias="type")


class VocaloidAudioTrack(VocaloidBaseTracks):
    parts: list[VocaloidWavPart] = Field(default_factory=list)
    type_value: Literal[VocaloidTrackType.AUDIO] = Field(VocaloidTrackType.AUDIO, alias="type")


VocaloidTracks = Annotated[
    Union[VocaloidStandardTrack, VocaloidAITrack, VocaloidAudioTrack],
    Field(discriminator="type_value"),
]


class VocaloidProject(BaseModel):
    master_track: VocaloidMasterTrack = Field(
        alias="masterTrack", default_factory=VocaloidMasterTrack
    )
    title: Optional[str] = ""
    tracks: list[VocaloidTracks] = Field(default_factory=list)
    vender: str = "Yamaha Corporation"
    version: Optional[VocaloidVersion] = Field(default_factory=VocaloidVersion)
    voices: list[VocaloidVoices] = Field(default_factory=list)
