import sys
from itertools import chain
from typing import Dict, List, Literal, NamedTuple, Optional
from uuid import uuid4

from setuptools.extern.more_itertools import chunked
from pydantic import Field, validator

from libresvip.core.time_interval import RangeInterval
from libresvip.model.base import BaseModel, PointList

from .interval_utils import position_to_ticks


def uuid_str():
    return str(uuid4())


class SVPoint(NamedTuple):
    offset: int
    value: float


class SVPoints(PointList[SVPoint]):
    pass


class SVBaseAttributes(BaseModel):
    t_f0_left: Optional[float] = Field(alias="tF0Left")
    t_f0_right: Optional[float] = Field(alias="tF0Right")
    d_f0_left: Optional[float] = Field(alias="dF0Left")
    d_f0_right: Optional[float] = Field(alias="dF0Right")
    t_f0_vbr_start: Optional[float] = Field(alias="tF0VbrStart")
    t_f0_vbr_left: Optional[float] = Field(alias="tF0VbrLeft")
    t_f0_vbr_right: Optional[float] = Field(alias="tF0VbrRight")
    d_f0_vbr: Optional[float] = Field(alias="dF0Vbr")
    f_f0_vbr: Optional[float] = Field(alias="fF0Vbr")
    param_loudness: Optional[float] = Field(alias="paramLoudness")
    param_tension: Optional[float] = Field(alias="paramTension")
    param_breathiness: Optional[float] = Field(alias="paramBreathiness")
    param_gender: Optional[float] = Field(alias="paramGender")
    param_tone_shift: Optional[float] = Field(alias="paramToneShift")
    improvise_attack_release: Optional[bool] = Field(alias="improviseAttackRelease")


class SVMeter(BaseModel):
    index: int
    denominator: int = 4
    numerator: int = 4


class SVTempo(BaseModel):
    bpm: float
    position: int


class SVTime(BaseModel):
    meter: List[SVMeter] = Field(default_factory=list)
    tempo: List[SVTempo] = Field(default_factory=list)


class SVParamCurve(BaseModel):
    mode: str = Field("linear", regex="linear|cubic|cosine|sigmoid")
    points: SVPoints = Field(default_factory=SVPoints)

    @validator("points", pre=True)
    def load_points(cls, points: List[float]):
        return SVPoints(__root__=[SVPoint(*each) for each in chunked(points, 2)])

    def _iter(
        self,
        **kwargs,
    ):
        for key, value in super()._iter(**kwargs):
            if key in {"points"}:
                yield key, list(chain.from_iterable(self.points.__root__))
            else:
                yield key, value

    def edited_range(self, default_value: float = 0.0) -> RangeInterval:
        tolerance = 1e-6
        interval = RangeInterval()
        points = [
            SVPoint(position_to_ticks(point.offset), point.value)
            for point in self.points
        ]
        if not points:
            return interval
        elif len(points) == 1:
            return (
                interval
                if abs(points[0].value - default_value) < tolerance
                else RangeInterval([(0, sys.maxsize // 2)])
            )
        if abs(points[0].value - default_value) > tolerance:
            interval |= RangeInterval([(0, points[0].offset)])
        start, end = points[0].offset, points[0].offset
        for i in range(1, len(points)):
            if (
                abs(points[i - 1].value - default_value) < tolerance
                and abs(points[i].value - default_value) < tolerance
            ):
                if start < end:
                    interval |= RangeInterval([(start, end)])
                start = points[i].offset
            else:
                end = points[i].offset
        if start < end:
            interval |= RangeInterval([(start, end)])
        if abs(points[-1].value - default_value) > tolerance:
            interval |= RangeInterval([(points[-1].offset, sys.maxsize // 2)])
        return interval

    def __add__(self, offset: int):
        new_curve = self.copy(deep=True)
        new_curve.points = new_curve.load_points(new_curve.points)
        for i in range(len(new_curve.points)):
            new_curve.points[i] = SVPoint(
                new_curve.points[i].offset + offset, new_curve.points[i].value
            )
        return new_curve


class SVNoteAttrConsts:
    default_pitch_transition = 0.0
    default_pitch_slide = 0.07
    default_pitch_depth = 0.15
    default_vibrato_start = 0.25
    default_vibrato_fade = 0.2
    default_vibrato_depth = 1.0
    default_vibrato_frequency = 5.5
    default_vibrato_phase = 0.0
    default_vibrato_jitter = 1.0
    system_pitch_slide = 0.1
    system_pitch_depth = 0.0


class SVParamTake(BaseModel):
    id: int
    expr: float
    liked: bool = False


class SVParamTakes(BaseModel):
    active_take_id: int = Field(alias="activeTakeId")
    takes: List[SVParamTake] = Field(default_factory=list)


class SVNoteAttributes(SVBaseAttributes):
    t_f0_offset: Optional[float] = Field(None, alias="tF0Offset")
    p_f0_vbr: float = Field(None, alias="pF0Vbr")
    d_f0_jitter: float = Field(None, alias="dF0Jitter")
    t_note_offset: float = Field(None, alias="tNoteOffset")
    dur: Optional[List[float]]
    alt: Optional[List[float]]
    expr_group: Optional[str] = Field(None, alias="exprGroup")
    strength: Optional[List[float]]
    r_tone: Optional[float] = Field(alias="rTone")
    r_intonation: Optional[float] = Field(alias="rIntonation")

    def _get_transition_offset(self) -> float:
        return (
            SVNoteAttrConsts.default_pitch_transition
            if self.t_f0_offset is None
            else self.t_f0_offset
        )

    def _set_transition_offset(self, value):
        self.t_f0_offset = value

    transition_offset = property(_get_transition_offset, _set_transition_offset)

    def _get_slide_left(self) -> float:
        return (
            SVNoteAttrConsts.default_pitch_slide
            if self.t_f0_left is None
            else self.t_f0_left
        )

    def _set_slide_left(self, value):
        self.t_f0_left = value

    slide_left = property(_get_slide_left, _set_slide_left)

    def _get_slide_right(self) -> float:
        return (
            SVNoteAttrConsts.default_pitch_slide
            if self.t_f0_right is None
            else self.t_f0_right
        )

    def _set_slide_right(self, value):
        self.t_f0_right = value

    slide_right = property(_get_slide_right, _set_slide_right)

    def _get_depth_left(self) -> float:
        return (
            SVNoteAttrConsts.default_pitch_depth
            if self.d_f0_left is None
            else self.d_f0_left
        )

    def _set_depth_left(self, value):
        self.d_f0_left = value

    depth_left = property(_get_depth_left, _set_depth_left)

    def _get_depth_right(self) -> float:
        return (
            SVNoteAttrConsts.default_pitch_depth
            if self.d_f0_right is None
            else self.d_f0_right
        )

    def _set_depth_right(self, value):
        self.d_f0_right = value

    depth_right = property(_get_depth_right, _set_depth_right)

    def _get_vibrato_start(self) -> float:
        return (
            SVNoteAttrConsts.default_vibrato_start
            if self.t_f0_vbr_start is None
            else self.t_f0_vbr_start
        )

    def _set_vibrato_start(self, value):
        self.t_f0_vbr_start = value

    vibrato_start = property(_get_vibrato_start, _set_vibrato_start)

    def _get_vibrato_left(self) -> float:
        return (
            SVNoteAttrConsts.default_vibrato_fade
            if self.t_f0_vbr_left is None
            else self.t_f0_vbr_left
        )

    def _set_vibrato_left(self, value):
        self.t_f0_vbr_left = value

    vibrato_left = property(_get_vibrato_left, _set_vibrato_left)

    def _get_vibrato_right(self) -> float:
        return (
            SVNoteAttrConsts.default_vibrato_fade
            if self.t_f0_vbr_right is None
            else self.t_f0_vbr_right
        )

    def _set_vibrato_right(self, value):
        self.t_f0_vbr_right = value

    vibrato_right = property(_get_vibrato_right, _set_vibrato_right)

    def _get_vibrato_depth(self) -> float:
        return (
            SVNoteAttrConsts.default_vibrato_depth
            if self.d_f0_vbr is None
            else self.d_f0_vbr
        )

    def _set_vibrato_depth(self, value):
        self.d_f0_vbr = value

    vibrato_depth = property(_get_vibrato_depth, _set_vibrato_depth)

    def _get_vibrato_frequency(self) -> float:
        return (
            SVNoteAttrConsts.default_vibrato_frequency
            if self.f_f0_vbr is None
            else self.f_f0_vbr
        )

    def _set_vibrato_frequency(self, value):
        self.f_f0_vbr = value

    vibrato_frequency = property(_get_vibrato_frequency, _set_vibrato_frequency)

    def _get_vibrato_phase(self) -> float:
        return (
            SVNoteAttrConsts.default_vibrato_phase
            if self.p_f0_vbr is None
            else self.p_f0_vbr
        )

    def _set_vibrato_phase(self, value):
        self.p_f0_vbr = value

    vibrato_phase = property(_get_vibrato_phase, _set_vibrato_phase)

    def _get_vibrato_jitter(self) -> float:
        return (
            SVNoteAttrConsts.default_vibrato_jitter
            if self.d_f0_jitter is None
            else self.d_f0_jitter
        )

    def _set_vibrato_jitter(self, value):
        self.d_f0_jitter = value

    vibrato_jitter = property(_get_vibrato_jitter, _set_vibrato_jitter)

    def set_phone_duration(self, index: int, duration: float):
        if self.dur is None:
            self.dur = [1.0] * (index + 1)
        elif len(self.dur) <= index:
            self.dur.extend([1.0] * (index - len(self.dur) + 1))
        self.dur[index] = duration

    def pitch_edited(
        self,
        regard_default_vibrato_as_unedited: bool = True,
        consider_instant_pitch_mode: bool = True,
    ) -> bool:
        transition_edited = any(
            x is not None
            for x in [
                self.t_f0_offset,
                self.t_f0_left,
                self.t_f0_right,
                self.d_f0_left,
                self.d_f0_right,
            ]
        )
        if consider_instant_pitch_mode:
            tolerance = 1e-6
            transition_edited &= any(
                x >= tolerance
                for x in (
                    abs(self.slide_left - SVNoteAttrConsts.default_pitch_slide),
                    abs(self.slide_right - SVNoteAttrConsts.default_pitch_slide),
                    abs(self.depth_left - SVNoteAttrConsts.default_pitch_depth),
                    abs(self.depth_right - SVNoteAttrConsts.default_pitch_depth),
                )
            )

        vibrato_edited = self.vibrato_depth != 0.0
        if regard_default_vibrato_as_unedited:
            vibrato_edited &= any(
                x is not None
                for x in (
                    self.d_f0_vbr,
                    self.f_f0_vbr,
                    self.p_f0_vbr,
                    self.t_f0_vbr_left,
                    self.t_f0_vbr_right,
                    self.t_f0_vbr_start,
                )
            )
        return transition_edited or vibrato_edited


class SVNote(BaseModel):
    onset: int
    duration: int
    lyrics: str = ""
    phonemes: str = ""
    pitch: int
    detune: Optional[int]
    accent: Optional[str]
    attributes: SVNoteAttributes = Field(default_factory=SVNoteAttributes)
    system_attributes: Optional[SVNoteAttributes] = Field(alias="systemAttributes")
    pitch_takes: Optional[SVParamTakes] = Field(alias="pitchTakes")
    timbre_takes: Optional[SVParamTakes] = Field(alias="timbreTakes")
    musical_type: Optional[Literal["singing", "rap"]] = Field(
        "singing", alias="musicalType"
    )
    instant_mode: Optional[bool] = Field(alias="instantMode")

    def cover_range(self):
        return RangeInterval([(self.onset, self.onset + self.duration)])

    def merge_attributes(self, attributes: SVNoteAttributes):
        ori_dict = self.attributes.dict(
            by_alias=True, exclude_none=True, exclude_unset=True, exclude_defaults=True
        )
        new_dict = attributes.dict(
            by_alias=True, exclude_none=True, exclude_unset=True, exclude_defaults=True
        )
        ori_dict.update({k: v for k, v in new_dict.items() if k not in ori_dict})
        self.attributes = SVNoteAttributes.parse_obj(ori_dict)

    def pitch_edited(
        self,
        regard_default_vibrato_as_unedited: bool = True,
        consider_instant_pitch_mode: bool = True,
    ) -> bool:
        return self.attributes.pitch_edited(
            regard_default_vibrato_as_unedited, consider_instant_pitch_mode
        )

    def __add__(self, blick_offset: int):
        return self.copy(deep=True, update={"onset": self.onset + blick_offset})

    def __xor__(self, pitch_offset: int):
        return self.copy(deep=True, update={"pitch": self.pitch + pitch_offset})


class SVRenderConfig(BaseModel):
    aspiration_format: str = Field("noAspiration", alias="aspirationFormat")
    bit_depth: int = Field(16, alias="bitDepth")
    destination: str = "./"
    filename: str = "untitled"
    num_channels: int = Field(1, alias="numChannels")
    sample_rate: int = Field(44100, alias="sampleRate")
    export_mix_down: bool = Field(True, alias="exportMixDown")
    export_pitch: Optional[bool] = Field(False, alias="exportPitch")


class SVParameters(BaseModel):
    breathiness: SVParamCurve = Field(default_factory=SVParamCurve, title="气声")
    gender: SVParamCurve = Field(default_factory=SVParamCurve, title="性别")
    loudness: SVParamCurve = Field(default_factory=SVParamCurve, title="响度")
    pitch_delta: SVParamCurve = Field(
        default_factory=SVParamCurve, alias="pitchDelta", title="音高偏差"
    )
    tension: SVParamCurve = Field(default_factory=SVParamCurve, title="张力")
    vibrato_env: SVParamCurve = Field(
        default_factory=SVParamCurve, alias="vibratoEnv", title="颤音包络"
    )
    voicing: SVParamCurve = Field(default_factory=SVParamCurve, title="发声")
    tone_shift: Optional[SVParamCurve] = Field(
        default_factory=SVParamCurve, alias="toneShift", title="音区偏移"
    )

    def __add__(self, offset: int):
        new_params = self.copy(deep=True)
        for key in new_params.__fields__:
            val = getattr(new_params, key, None)
            if val is not None:
                setattr(new_params, key, val + offset)
        return new_params


class SVVoice(SVBaseAttributes):
    vocal_mode_inherited: bool = Field(True, alias="vocalModeInherited")
    vocal_mode_preset: str = Field("", alias="vocalModePreset")
    vocal_mode_params: Optional[dict] = Field(alias="vocalModeParams")
    render_mode: Optional[str] = Field(alias="renderMode")

    def to_attributes(self) -> SVNoteAttributes:
        voice_dict = self.dict(
            by_alias=True,
            exclude_none=True,
            exclude_unset=True,
            exclude={
                "vocal_mode_inherited",
                "vocal_mode_preset",
                "vocal_mode_params",
                "render_mode",
                "improvise_attack_release",
            },
        )
        return SVNoteAttributes.parse_obj(voice_dict)


class SVAudio(BaseModel):
    filename: str = ""
    duration: float


class SVDatabase(BaseModel):
    name: str = ""
    language: str = ""
    phoneset: str = ""
    version: Optional[str]
    language_override: str = Field("", alias="languageOverride")
    phoneset_override: str = Field("", alias="phonesetOverride")
    backend_type: str = Field("", alias="backendType")


class SVRef(BaseModel):
    audio: Optional[SVAudio]
    blick_offset: int = Field(default=0, alias="blickOffset")
    pitch_offset: int = Field(default=0, alias="pitchOffset")
    pitch_takes: Optional[SVParamTakes] = Field(alias="pitchTakes")
    timbre_takes: Optional[SVParamTakes] = Field(alias="timbreTakes")
    database: SVDatabase = Field(default_factory=SVDatabase)
    dictionary: str = ""
    voice: SVVoice = Field(default_factory=SVVoice)
    group_id: str = Field(default_factory=uuid_str, alias="groupID")
    is_instrumental: bool = Field(default=False, alias="isInstrumental")
    system_pitch_delta: SVParamCurve = Field(
        default_factory=SVParamCurve, alias="systemPitchDelta"
    )


class SVGroup(BaseModel):
    name: str = "main"
    notes: List[SVNote] = Field(default_factory=list)
    parameters: SVParameters = Field(default_factory=SVParameters)
    uuid: str = Field(default_factory=uuid_str)
    vocal_modes: Dict[str, SVParamCurve] = Field(
        default_factory=dict, alias="vocalModes"
    )

    @validator("notes", pre=True)
    def validate_notes(cls, v):
        v = [note for note in v if note["onset"] >= 0]
        return v

    def overlapped_with(self, other: "SVGroup") -> bool:
        for note in self.notes:
            for other_note in other.notes:
                x = note.onset - (other_note.onset + other_note.duration)
                y = (note.onset + note.duration) - other_note.onset
                if x * y == 0:
                    continue
                tmp = (x < 0) ^ (y > 0)
                if tmp:
                    return True
        return False

    def __add__(self, blick_offset: int):
        new_group = self.copy(deep=True)
        new_group.notes = [
            note + blick_offset for note in self.notes if note.onset + blick_offset >= 0
        ]
        new_group.parameters += blick_offset
        return new_group

    def __xor__(self, pitch_offset):
        new_group = self.copy(deep=True)
        for note in new_group.notes:
            note ^= pitch_offset
        return new_group


class SVMixer(BaseModel):
    pan: float
    mute: bool
    solo: bool
    display: bool = True
    gain_decibel: float = Field(alias="gainDecibel")


class SVTrack(BaseModel):
    disp_color: str = Field(default="ff7db235", alias="dispColor")
    disp_order: int = Field(default=0, alias="dispOrder")
    groups: List[SVRef] = Field(default_factory=list)
    main_group: SVGroup = Field(default_factory=SVGroup, alias="mainGroup")
    main_ref: SVRef = Field(default_factory=SVRef, alias="mainRef")
    mixer: SVMixer = Field(default_factory=SVMixer)
    name: str = "Track 1"
    render_enabled: bool = Field(default=True, alias="renderEnabled")


class SVProject(BaseModel):
    library: List[SVGroup] = Field(default_factory=list)
    render_config: SVRenderConfig = Field(
        default_factory=SVRenderConfig, alias="renderConfig"
    )
    instant_mode_enabled: Optional[bool] = Field(alias="instantModeEnabled")
    time_sig: SVTime = Field(default_factory=SVTime, alias="time")
    tracks: List[SVTrack] = Field(default_factory=list)
    version: int = 113
