import enum
from dataclasses import dataclass
from typing import Annotated, Literal

from pydantic import ConfigDict, Field, ValidationInfo, create_model, model_validator
from typing_extensions import Self

from libresvip.model.base import BaseModel
from libresvip.utils.translation import gettext_lazy as _


class VocaloidLanguage(enum.IntEnum):
    _value_: Annotated[
        int,
        create_model(
            "VocaloidLanguage",
            __module__="libresvip.plugins.vpr.model",
            JAPANESE=(int, Field(title=_("日本語"))),
            ENGLISH=(int, Field(title=_("English"))),
            KOREAN=(int, Field(title=_("한국어"))),
            SPANISH=(int, Field(title=_("Español"))),
            SIMPLIFIED_CHINESE=(int, Field(title=_("简体中文"))),
        ),
    ]
    JAPANESE = 0
    ENGLISH = 1
    KOREAN = 2
    SPANISH = 3
    SIMPLIFIED_CHINESE = 4


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
    duration: int | None = None


class VocaloidPoint(VocaloidBasePos):
    value: int | float | Literal["ZeroPitch"] | None = None


class VocaloidTimeSig(BaseModel):
    bar: int = 0
    denom: int = 4
    numer: int = 4


class VocaloidExp(BaseModel):
    opening: int | None = 127
    accent: int | None = None
    decay: int | None = None
    bend_depth: int | None = Field(None, alias="bendDepth")
    bend_length: int | None = Field(None, alias="bendLength")


class VocaloidAIExp(BaseModel):
    pitch_fine: float | None = Field(None, alias="pitchFine")
    pitch_drift_start: float | None = Field(None, alias="pitchDriftStart")
    pitch_drift_end: float | None = Field(None, alias="pitchDriftEnd")
    pitch_scaling_center: float | None = Field(None, alias="pitchScalingCenter")
    pitch_scaling_origin: float | None = Field(None, alias="pitchScalingOrigin")
    pitch_transition_start: float | None = Field(None, alias="pitchTransitionStart")
    pitch_transition_end: float | None = Field(None, alias="pitchTransitionEnd")
    amplitude_whole: float | None = Field(None, alias="amplitudeWhole")
    amplitude_start: float | None = Field(None, alias="amplitudeStart")
    amplitude_end: float | None = Field(None, alias="amplitudeEnd")
    formant_whole: float | None = Field(None, alias="formantWhole")
    formant_start: float | None = Field(None, alias="formantStart")
    formant_end: float | None = Field(None, alias="formantEnd")
    vibrato_leading_depth: float | None = Field(None, alias="vibratoLeadingDepth")
    vibrato_following_depth: float | None = Field(None, alias="vibratoFollowingDepth")


class VocaloidEnabled(BaseModel):
    is_enabled: bool | None = Field(True, alias="isEnabled")


class VocaloidGlobal(VocaloidEnabled):
    value: int | None = 12000


class VocaloidRegion(VocaloidEnabled):
    begin: float | None = 0
    end: float | None = 7680


class VocaloidParameters(BaseModel):
    name: str | None = None
    value: int | float | str | None = None


class VocaloidVersion(BaseModel):
    major: int = 5
    minor: int = 0
    revision: int = 0


class VocaloidVibrato(BaseModel):
    type_value: int | None = Field(0, alias="type")
    duration: int | None = 0
    depths: list[VocaloidPoint] | None = Field(default_factory=list)
    rates: list[VocaloidPoint] | None = Field(default_factory=list)


class VocaloidCompID(BaseModel):
    comp_id: str | None = Field(None, alias="compID")


class VocaloidLangID(BaseModel):
    lang_id: VocaloidLanguage | None = Field(VocaloidLanguage.SIMPLIFIED_CHINESE, alias="langID")


class VocaloidVoice(VocaloidCompID, VocaloidLangID):
    pass


class VocaloidAIVoice(VocaloidCompID):
    lang_ids: list[VocaloidLangID] = Field(default_factory=list, alias="langIDs")


class VocaloidVoices(VocaloidCompID):
    name: str | None = None


class VocaloidWeight(BaseModel):
    pre: int | None = 64
    post: int | None = 64


class VocaloidControllers(BaseModel):
    name: str | None = None
    events: list[VocaloidPoint] = Field(default_factory=list)


class VocaloidFolded(BaseModel):
    is_folded: bool | None = Field(True, alias="isFolded")


class VocaloidEffects(VocaloidFolded):
    id_value: str | None = Field(None, alias="id")
    is_bypassed: bool | None = Field(None, alias="isBypassed")
    parameters: list[VocaloidParameters] = Field(default_factory=list)


class VocaloidSingingSkill(BaseModel):
    duration: int | None = 158
    weight: VocaloidWeight | None = Field(default_factory=VocaloidWeight)


class VocaloidTempo(VocaloidFolded):
    events: list[VocaloidPoint] = Field(default_factory=list)
    global_value: VocaloidGlobal | None = Field(alias="global", default_factory=VocaloidGlobal)
    height: float | None = 0
    ara: VocaloidEnabled | None = None


class VocaloidTimeSigs(VocaloidFolded):
    events: list[VocaloidTimeSig] = Field(default_factory=list)


class VocaloidAutomation(VocaloidFolded):
    height: float | None = 0
    events: list[VocaloidPoint] = Field(default_factory=list)


class VocaloidMasterTrack(BaseModel):
    loop: VocaloidRegion = Field(default_factory=VocaloidRegion)
    sampling_rate: int = Field(44100, alias="samplingRate")
    tempo: VocaloidTempo = Field(default_factory=VocaloidTempo)
    time_sig: VocaloidTimeSigs = Field(alias="timeSig", default_factory=VocaloidTimeSigs)
    volume: VocaloidAutomation = Field(default_factory=VocaloidAutomation)
    main_tuning: float = Field(440, alias="mainTuning")


class VocaloidDVQMRelease(VocaloidCompID):
    speed: int | None = None
    level_names: list[str] | None = Field(None, alias="levelNames")
    top_factor: float | None = Field(None, alias="topFactor")
    is_protected: bool | None = Field(None, alias="isProtected")


class VocaloidDVQM(BaseModel):
    release: VocaloidDVQMRelease | None = None
    attack: VocaloidDVQMRelease | None = None


class VocaloidNotes(VocaloidLangID, VocaloidWithDur):
    exp: VocaloidExp | None = Field(default_factory=VocaloidExp)
    ai_exp: VocaloidAIExp | None = Field(None, alias="aiExp")
    direct_pitches: list[VocaloidPoint] | None = Field(None, alias="directPitches")
    is_protected: bool | None = Field(False, alias="isProtected")
    is_ai_vibrato_enabled: bool | None = Field(False, alias="isAiVibratoEnabled")
    lyric: str
    number: int
    phoneme: str | None = None
    phoneme_positions: list[VocaloidBasePos] | None = Field(None, alias="phonemePositions")
    singing_skill: VocaloidSingingSkill | None = Field(
        alias="singingSkill", default_factory=VocaloidSingingSkill
    )
    velocity: int = 64
    vibrato: VocaloidVibrato | None = Field(default_factory=VocaloidVibrato)
    dvqm: VocaloidDVQM | None = None


class VocaloidWav(BaseModel):
    name: str
    original_name: str | None = Field(None, alias="originalName")

    @model_validator(mode="after")
    def extract_audio(self, info: ValidationInfo) -> Self:
        if (
            info.context is not None
            and info.context["extract_audio"]
            and not hasattr(info.context["path"], "protocol")
        ):
            archive_wav_path = f"Project/Audio/{self.name}"
            if not (
                wav_path := (info.context["path"].parent / (self.original_name or self.name))
            ).exists():
                wav_path.write_bytes((info.context["archive_file"] / archive_wav_path).read_bytes())
        return self


class VocaloidVoicePart(VocaloidWithDur):
    name: str | None = ""
    midi_effects: list[VocaloidEffects] = Field(default_factory=list, alias="midiEffects")
    audio_effects: list[VocaloidEffects] = Field(default_factory=list, alias="audioEffects")
    notes: list[VocaloidNotes] = Field(default_factory=list)
    style_preset_id: str | None = Field(None, alias="stylePresetID")
    style_name: str | None = Field("No Effect", alias="styleName")
    voice: VocaloidVoice | None = None
    secondary_voice: VocaloidVoice | None = Field(None, alias="secondaryVoice")
    ai_voice: VocaloidAIVoice | None = Field(None, alias="aiVoice")
    controllers: list[VocaloidControllers] | None = None

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
    region: VocaloidRegion | None = None
    name: str | None = ""
    wav: VocaloidWav | None = None


class VocaloidBaseTracks(VocaloidFolded):
    bus_no: int | None = Field(0, alias="busNo")
    color: int | None = 0
    height: float | None = 0
    is_muted: bool = Field(False, alias="isMuted")
    is_solo_mode: bool = Field(False, alias="isSoloMode")
    name: str | None = ""
    panpot: VocaloidAutomation = Field(default_factory=VocaloidAutomation)
    volume: VocaloidAutomation = Field(default_factory=VocaloidAutomation)
    last_scroll_position_note_number: int | None = Field(None, alias="lastScrollPositionNoteNumber")
    audio_effects: list[VocaloidEffects] = Field(default_factory=list, alias="audioEffects")


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
    VocaloidStandardTrack | VocaloidAITrack | VocaloidAudioTrack,
    Field(discriminator="type_value"),
]


class VocaloidProject(BaseModel):
    master_track: VocaloidMasterTrack = Field(
        alias="masterTrack", default_factory=VocaloidMasterTrack
    )
    title: str | None = ""
    tracks: list[VocaloidTracks] = Field(default_factory=list)
    vender: str = "Yamaha Corporation"
    version: VocaloidVersion | None = Field(default_factory=VocaloidVersion)
    voices: list[VocaloidVoices] = Field(default_factory=list)
