from __future__ import annotations

import re
import sys
from itertools import chain
from typing import Any, Literal, NamedTuple, Optional, Union
from uuid import uuid4

import zhon
from more_itertools import batched
from pydantic import (
    Field,
    FieldSerializationInfo,
    RootModel,
    ValidationInfo,
    field_serializer,
    field_validator,
    model_validator,
)
from retrie.retrie import Blacklist
from typing_extensions import Self

from libresvip.core.constants import DEFAULT_PHONEME
from libresvip.core.time_interval import RangeInterval
from libresvip.model.base import BaseModel, Note
from libresvip.model.point import PointList
from libresvip.utils.audio import audio_path_validator

from . import constants
from .interval_utils import position_to_ticks

symbols_blacklist = Blacklist(
    [
        "(",
        ")",
        "[",
        "]",
        "{",
        "}",
        "（",
        "）",
        "<",
        ">",
        "《",
        "》",
        "―",
        "—",
        "*",
        "×",
        "!",
        "！",
        "?",
        "？",
        ":",
        "：",
        "·",
        "•",
        "。",
        ",",
        "，",
        ";",
        "；",
        "^",
        "`",
        '"',
        "‘",
        "’",
        "“",
        "”",
        "=",
        "、",
        "_",
        "$",
        "%",
        "~",
        "@",
        "#",
        "…",
        "&",
        "￥",
    ],
    match_substrings=True,
)


def uuid_str() -> str:
    return str(uuid4())


class SVPoint(NamedTuple):
    offset: int
    value: float


class SVPoints(PointList[SVPoint], RootModel[list[SVPoint]]):
    root: list[SVPoint] = Field(default_factory=list)


class SVBaseAttributes(BaseModel):
    t_f0_left: Optional[float] = Field(None, alias="tF0Left")
    t_f0_right: Optional[float] = Field(None, alias="tF0Right")
    d_f0_left: Optional[float] = Field(None, alias="dF0Left")
    d_f0_right: Optional[float] = Field(None, alias="dF0Right")
    t_f0_vbr_start: Optional[float] = Field(None, alias="tF0VbrStart")
    t_f0_vbr_left: Optional[float] = Field(None, alias="tF0VbrLeft")
    t_f0_vbr_right: Optional[float] = Field(None, alias="tF0VbrRight")
    d_f0_vbr: Optional[float] = Field(None, alias="dF0Vbr")
    f_f0_vbr: Optional[float] = Field(None, alias="fF0Vbr")
    param_loudness: Optional[float] = Field(None, alias="paramLoudness")
    param_tension: Optional[float] = Field(None, alias="paramTension")
    param_breathiness: Optional[float] = Field(None, alias="paramBreathiness")
    param_gender: Optional[float] = Field(None, alias="paramGender")
    param_tone_shift: Optional[float] = Field(None, alias="paramToneShift")
    improvise_attack_release: Optional[bool] = Field(None, alias="improviseAttackRelease")
    language_override: Optional[str] = Field(None, alias="languageOverride")
    phoneset_override: Optional[str] = Field(None, alias="phonesetOverride")


class SVMeter(BaseModel):
    index: int
    denominator: int = 4
    numerator: int = 4


class SVTempo(BaseModel):
    bpm: float
    position: int


class SVTime(BaseModel):
    meter: list[SVMeter] = Field(default_factory=list)
    tempo: list[SVTempo] = Field(default_factory=list)


class SVParamCurve(BaseModel):
    mode: Literal["linear", "cubic", "cosine", "sigmoid"] = Field("linear")
    points: SVPoints = Field(default_factory=SVPoints)

    @field_validator("points", mode="before")
    @classmethod
    def validate_points(cls, points: list[float], _info: ValidationInfo) -> SVPoints:
        if _info.mode == "json":
            return SVPoints(root=[SVPoint._make(each) for each in batched(points, 2)])
        return SVPoints(root=points)

    @field_serializer("points", when_used="json")
    def serialize_points(self, points: SVPoints, _info: FieldSerializationInfo) -> list[float]:
        return list(chain.from_iterable(points.root))

    def edited_range(self, default_value: float = 0.0) -> RangeInterval:
        tolerance = 1e-6
        interval = RangeInterval()
        points = [
            SVPoint(position_to_ticks(point.offset), point.value) for point in self.points.root
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

    def __add__(self, offset: int) -> SVParamCurve:
        new_curve = self.model_copy(deep=True)
        for i in range(len(new_curve.points)):
            new_curve.points[i] = new_curve.points[i]._replace(
                offset=new_curve.points[i].offset + offset
            )
        return new_curve


class SVParamTake(BaseModel):
    id_value: int = Field(alias="id")
    expr: float
    liked: bool = False


class SVParamTakes(BaseModel):
    active_take_id: int = Field(alias="activeTakeId")
    takes: list[SVParamTake] = Field(default_factory=list)


class SVNoteAttributes(SVBaseAttributes):
    t_f0_left: Optional[float] = Field(None, alias="tF0Left")
    t_f0_right: Optional[float] = Field(None, alias="tF0Right")
    d_f0_left: Optional[float] = Field(None, alias="dF0Left")
    d_f0_right: Optional[float] = Field(None, alias="dF0Right")
    t_f0_vbr_start: Optional[float] = Field(None, alias="tF0VbrStart")
    t_f0_vbr_left: Optional[float] = Field(None, alias="tF0VbrLeft")
    t_f0_vbr_right: Optional[float] = Field(None, alias="tF0VbrRight")
    d_f0_vbr: Optional[float] = Field(None, alias="dF0Vbr")
    f_f0_vbr: Optional[float] = Field(None, alias="fF0Vbr")
    t_f0_offset: Optional[float] = Field(None, alias="tF0Offset")
    p_f0_vbr: Optional[float] = Field(None, alias="pF0Vbr")
    d_f0_jitter: Optional[float] = Field(None, alias="dF0Jitter")
    t_note_offset: Optional[float] = Field(None, alias="tNoteOffset")
    dur: Optional[list[float]] = None
    alt: Optional[list[float]] = None
    expr_group: Optional[str] = Field(None, alias="exprGroup")
    strength: Optional[list[float]] = None
    r_tone: Optional[float] = Field(None, alias="rTone")
    r_intonation: Optional[float] = Field(None, alias="rIntonation")
    even_syllable_duration: Optional[float] = Field(None, alias="evenSyllableDuration")

    def _get_transition_offset(self) -> float:
        return constants.DEFAULT_PITCH_TRANSITION if self.t_f0_offset is None else self.t_f0_offset

    def _set_transition_offset(self, value: float) -> None:
        self.t_f0_offset = value

    transition_offset = property(_get_transition_offset, _set_transition_offset)

    def _get_portamento_left(self) -> float:
        return constants.DEFAULT_PITCH_PORTAMENTO if self.t_f0_left is None else self.t_f0_left

    def _set_portamento_left(self, value: float) -> None:
        self.t_f0_left = value

    portamento_left = property(_get_portamento_left, _set_portamento_left)

    def _get_portamento_right(self) -> float:
        return constants.DEFAULT_PITCH_PORTAMENTO if self.t_f0_right is None else self.t_f0_right

    def _set_portamento_right(self, value: float) -> None:
        self.t_f0_right = value

    portamento_right = property(_get_portamento_right, _set_portamento_right)

    def _get_depth_left(self) -> float:
        return constants.DEFAULT_PITCH_DEPTH if self.d_f0_left is None else self.d_f0_left

    def _set_depth_left(self, value: float) -> None:
        self.d_f0_left = value

    depth_left = property(_get_depth_left, _set_depth_left)

    def _get_depth_right(self) -> float:
        return constants.DEFAULT_PITCH_DEPTH if self.d_f0_right is None else self.d_f0_right

    def _set_depth_right(self, value: float) -> None:
        self.d_f0_right = value

    depth_right = property(_get_depth_right, _set_depth_right)

    def _get_vibrato_start(self) -> float:
        return (
            constants.DEFAULT_VIBRATO_START if self.t_f0_vbr_start is None else self.t_f0_vbr_start
        )

    def _set_vibrato_start(self, value: float) -> None:
        self.t_f0_vbr_start = value

    vibrato_start = property(_get_vibrato_start, _set_vibrato_start)

    def _get_vibrato_left(self) -> float:
        return constants.DEFAULT_VIBRATO_FADE if self.t_f0_vbr_left is None else self.t_f0_vbr_left

    def _set_vibrato_left(self, value: float) -> None:
        self.t_f0_vbr_left = value

    vibrato_left = property(_get_vibrato_left, _set_vibrato_left)

    def _get_vibrato_right(self) -> float:
        return (
            constants.DEFAULT_VIBRATO_FADE if self.t_f0_vbr_right is None else self.t_f0_vbr_right
        )

    def _set_vibrato_right(self, value: float) -> None:
        self.t_f0_vbr_right = value

    vibrato_right = property(_get_vibrato_right, _set_vibrato_right)

    def _get_vibrato_depth(self) -> float:
        return constants.DEFAULT_VIBRATO_DEPTH if self.d_f0_vbr is None else self.d_f0_vbr

    def _set_vibrato_depth(self, value: float) -> None:
        self.d_f0_vbr = value

    vibrato_depth = property(_get_vibrato_depth, _set_vibrato_depth)

    def _get_vibrato_frequency(self) -> float:
        return constants.DEFAULT_VIBRATO_FREQUENCY if self.f_f0_vbr is None else self.f_f0_vbr

    def _set_vibrato_frequency(self, value: float) -> None:
        self.f_f0_vbr = value

    vibrato_frequency = property(_get_vibrato_frequency, _set_vibrato_frequency)

    def _get_vibrato_phase(self) -> float:
        return constants.DEFAULT_VIBRATO_PHASE if self.p_f0_vbr is None else self.p_f0_vbr

    def _set_vibrato_phase(self, value: float) -> None:
        self.p_f0_vbr = value

    vibrato_phase = property(_get_vibrato_phase, _set_vibrato_phase)

    def _get_vibrato_jitter(self) -> float:
        return constants.DEFAULT_VIBRATO_JITTER if self.d_f0_jitter is None else self.d_f0_jitter

    def _set_vibrato_jitter(self, value: float) -> None:
        self.d_f0_jitter = value

    vibrato_jitter = property(_get_vibrato_jitter, _set_vibrato_jitter)

    def set_phone_duration(self, index: int, duration: float) -> None:
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
                    abs(self.portamento_left - constants.DEFAULT_PITCH_PORTAMENTO),
                    abs(self.portamento_right - constants.DEFAULT_PITCH_PORTAMENTO),
                    abs(self.depth_left - constants.DEFAULT_PITCH_DEPTH),
                    abs(self.depth_right - constants.DEFAULT_PITCH_DEPTH),
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

    def default_language(self, database: SVDatabase) -> str:
        return self.language_override or database.language_override or database.language


class SVNote(BaseModel):
    onset: int
    duration: int
    lyrics: str = ""
    phonemes: str = ""
    pitch: int
    detune: Optional[int] = None
    accent: Optional[str] = None
    attributes: SVNoteAttributes = Field(default_factory=SVNoteAttributes)
    system_attributes: Optional[SVNoteAttributes] = Field(None, alias="systemAttributes")
    pitch_takes: Optional[SVParamTakes] = Field(None, alias="pitchTakes")
    timbre_takes: Optional[SVParamTakes] = Field(None, alias="timbreTakes")
    musical_type: Optional[Literal["singing", "rap"]] = Field("singing", alias="musicalType")
    instant_mode: Optional[bool] = Field(None, alias="instantMode")

    def merge_attributes(self, attributes: SVNoteAttributes) -> None:
        ori_dict = self.attributes.model_dump(
            by_alias=True,
            exclude_none=True,
            exclude_unset=True,
            exclude_defaults=True,
        )
        new_dict = attributes.model_dump(
            by_alias=True,
            exclude_none=True,
            exclude_unset=True,
            exclude_defaults=True,
        )
        ori_dict.update({k: v for k, v in new_dict.items() if k not in ori_dict})
        self.attributes = SVNoteAttributes.model_validate(ori_dict)

    @model_validator(mode="after")
    def _merge_system_attribute(self) -> Self:
        if self.system_attributes is not None:
            self.merge_attributes(self.system_attributes)
        return self

    def pitch_edited(
        self,
        regard_default_vibrato_as_unedited: bool = True,
        consider_instant_pitch_mode: bool = True,
    ) -> bool:
        return self.attributes.pitch_edited(
            regard_default_vibrato_as_unedited,
            consider_instant_pitch_mode and self.instant_mode is not False,
        )

    def __add__(self, blick_offset: int) -> SVNote:
        return self.model_copy(deep=True, update={"onset": self.onset + blick_offset})

    def __xor__(self, pitch_offset: int) -> SVNote:
        return self.model_copy(deep=True, update={"pitch": self.pitch + pitch_offset})

    @staticmethod
    def normalize_lyric(lyric: str) -> str:
        return symbols_blacklist.cleanse_text(lyric).strip()

    @classmethod
    def normalize_phoneme(cls, note: Note) -> str:
        if note.pronunciation:
            return note.pronunciation
        elif (hanzi := re.search(rf"[{zhon.hanzi.characters}]+", note.lyric)) is not None:
            return hanzi[0]
        elif valid_chars := cls.normalize_lyric(note.lyric):
            return valid_chars.lstrip(".")
        else:
            return DEFAULT_PHONEME


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

    def __add__(self, offset: int) -> SVParameters:
        new_params = self.model_copy(deep=True)
        for key in new_params.model_fields:
            if (val := getattr(new_params, key, None)) is not None:
                setattr(new_params, key, val + offset)
        return new_params


class SVVoice(SVBaseAttributes):
    t_f0_left: Optional[float] = Field(0.07, alias="tF0Left")
    t_f0_right: Optional[float] = Field(0.07, alias="tF0Right")
    d_f0_left: Optional[float] = Field(0.15, alias="dF0Left")
    d_f0_right: Optional[float] = Field(0.15, alias="dF0Right")
    t_f0_vbr_start: Optional[float] = Field(0.25, alias="tF0VbrStart")
    t_f0_vbr_left: Optional[float] = Field(0.2, alias="tF0VbrLeft")
    t_f0_vbr_right: Optional[float] = Field(0.2, alias="tF0VbrRight")
    d_f0_vbr: Optional[float] = Field(1.0, alias="dF0Vbr")
    f_f0_vbr: Optional[float] = Field(5.5, alias="fF0Vbr")
    vocal_mode_inherited: bool = Field(True, alias="vocalModeInherited")
    vocal_mode_preset: str = Field("", alias="vocalModePreset")
    vocal_mode_params: Optional[dict[str, float]] = Field(None, alias="vocalModeParams")
    render_mode: Optional[str] = Field(None, alias="renderMode")

    def to_attributes(self) -> SVNoteAttributes:
        voice_dict = self.model_dump(
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
        return SVNoteAttributes.model_validate(voice_dict)


class SVAudio(BaseModel):
    filename: str = ""
    duration: float

    validate_filename = field_validator("filename", mode="before")(audio_path_validator)


class SVDatabase(BaseModel):
    name: str = ""
    language: str = "mandarin"
    phoneset: str = "xsampa"
    version: Optional[Union[str, int]] = None
    language_override: Optional[str] = Field(None, alias="languageOverride")
    phoneset_override: Optional[str] = Field(None, alias="phonesetOverride")
    backend_type: str = Field("", alias="backendType")


class SVRef(BaseModel):
    audio: Optional[SVAudio] = None
    blick_absolute_begin: Optional[int] = Field(0, alias="blickAbsoluteBegin")
    blick_absolute_end: Optional[int] = Field(-1, alias="blickAbsoluteEnd")
    blick_offset: int = Field(default=0, alias="blickOffset")
    pitch_offset: int = Field(default=0, alias="pitchOffset")
    pitch_takes: Optional[SVParamTakes] = Field(None, alias="pitchTakes")
    timbre_takes: Optional[SVParamTakes] = Field(None, alias="timbreTakes")
    database: SVDatabase = Field(default_factory=SVDatabase)
    dictionary: str = ""
    voice: SVVoice = Field(default_factory=SVVoice)
    group_id: str = Field(default_factory=uuid_str, alias="groupID")
    is_instrumental: bool = Field(default=False, alias="isInstrumental")
    system_pitch_delta: SVParamCurve = Field(default_factory=SVParamCurve, alias="systemPitchDelta")


class SVGroup(BaseModel):
    name: str = "main"
    notes: list[SVNote] = Field(default_factory=list)
    parameters: SVParameters = Field(default_factory=SVParameters)
    uuid: str = Field(default_factory=uuid_str)
    vocal_modes: dict[str, SVParamCurve] = Field(default_factory=dict, alias="vocalModes")

    @field_validator("notes", mode="before")
    @classmethod
    def validate_notes(cls, v: list[dict[str, Any]], _info: ValidationInfo) -> list[dict[str, Any]]:
        return [note for note in v if note["onset"] >= 0]

    def overlapped_with(self, other: SVGroup) -> bool:
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

    def __add__(self, blick_offset: int) -> SVGroup:
        new_group = self.model_copy(deep=True)
        new_group.notes = [
            note + blick_offset for note in self.notes if note.onset + blick_offset >= 0
        ]
        new_group.parameters += blick_offset
        return new_group

    def __xor__(self, pitch_offset: int) -> SVGroup:
        new_group = self.model_copy(deep=True)
        for note in new_group.notes:
            note ^= pitch_offset
        return new_group


class SVMixer(BaseModel):
    pan: float = 0.0
    mute: bool = False
    solo: bool = False
    display: bool = True
    gain_decibel: float = Field(0.0, alias="gainDecibel")


class SVTrack(BaseModel):
    disp_color: str = Field(default="ff7db235", alias="dispColor")
    disp_order: int = Field(default=0, alias="dispOrder")
    groups: list[SVRef] = Field(default_factory=list)
    main_group: SVGroup = Field(default_factory=SVGroup, alias="mainGroup")
    main_ref: SVRef = Field(default_factory=SVRef, alias="mainRef")
    mixer: SVMixer = Field(default_factory=SVMixer)
    name: str = "Track 1"
    render_enabled: bool = Field(default=True, alias="renderEnabled")


class SVProject(BaseModel):
    library: list[SVGroup] = Field(default_factory=list)
    render_config: SVRenderConfig = Field(default_factory=SVRenderConfig, alias="renderConfig")
    instant_mode_enabled: Optional[bool] = Field(None, alias="instantModeEnabled")
    time_sig: SVTime = Field(default_factory=SVTime, alias="time")
    tracks: list[SVTrack] = Field(default_factory=list)
    version: int = 100
