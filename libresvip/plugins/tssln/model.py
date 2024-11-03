# mypy: disable-error-code="attr-defined"
from __future__ import annotations

import enum
from types import GenericAlias
from typing import Annotated, Any, Literal, Optional, Union, get_args

from packaging.version import Version
from pydantic import AliasChoices, Field, ValidationInfo, field_validator

from libresvip.core.exceptions import UnsupportedProjectVersionError
from libresvip.model.base import BaseModel
from libresvip.utils.translation import gettext_lazy as _

from .value_tree import JUCENode, JUCEVarTypes


class VoiSonaPlayControlItem(BaseModel):
    loop: bool = Field(alias="Loop")
    loop_start: float = Field(0, alias="LoopStart")
    loop_end: float = Field(alias="LoopEnd")
    play_position: float = Field(alias="PlayPosition")


class VoiSonaSongEditorItem(BaseModel):
    editor_width: int = Field(1920, alias="EditorWidth")
    editor_height: int = Field(1080, alias="EditorHeight")


class VoiSonaControlPanelStatus(BaseModel):
    quantization: int = Field(alias="Quantization")
    edit_tool: Optional[int] = Field(None, alias="EditTool")
    record_note: bool = Field(True, alias="RecordNote")
    record_tempo: bool = Field(True, alias="RecordTempo")


class VoiSonaAdjustToolBarStatus(BaseModel):
    main_panel: int = Field(alias="MainPanel")
    sub_panel: int = Field(alias="SubPanel")


class VoiSonaPanelControllerStatus(BaseModel):
    tempo_panel: Optional[bool] = Field(None, alias="TempoPanel")
    beat_panel: Optional[bool] = Field(None, alias="BeatPanel")
    key_panel: Optional[bool] = Field(None, alias="KeyPanel")
    dynamics_panel: Optional[bool] = Field(None, alias="DynamicsPanel")


class VoiSonaMainPanelStatus(VoiSonaPanelControllerStatus):
    scale_x: float = Field(alias="ScaleX_V2", validation_alias=AliasChoices("ScaleX_V2", "ScaleX"))
    scale_y: float = Field(alias="ScaleY_V2", validation_alias=AliasChoices("ScaleY_V2", "ScaleY"))
    scroll_x: Optional[float] = Field(None, alias="ScrollX")
    scroll_y: Optional[float] = Field(None, alias="ScrollY")


class VoiSonaNeuralVocoderInformation(BaseModel):
    nv_file_name: str = Field(alias="NVFileName")
    nv_lib_file_name: Optional[str] = Field(None, alias="NVLibFileName")
    nv_version: str = Field(alias="NVVersion")
    nv_hash: Optional[str] = Field(None, alias="NVHash")
    nv_lib_hash: Optional[str] = Field(None, alias="NVLibHash")
    nv_label: str = Field(alias="NVLabel")


class VoiSonaNeuralVocoderListItem(BaseModel):
    neural_vocoder_information: Optional[list[VoiSonaNeuralVocoderInformation]] = Field(
        None, alias="NeuralVocoderInformation"
    )


class VoiSonaEmotionItem(BaseModel):
    label: str = Field(alias="Label")
    ratio: float = Field(alias="Ratio")


class VoiSonaEmotionListItem(BaseModel):
    emotion: list[VoiSonaEmotionItem] = Field(default_factory=list, alias="Emotion")


class VoiSonaVoiceInformation(BaseModel):
    neural_vocoder_list: list[VoiSonaNeuralVocoderListItem] = Field(
        default_factory=list, alias="NeuralVocoderList"
    )
    emotion_list: list[VoiSonaEmotionListItem] = Field(default_factory=list, alias="EmotionList")
    character_name: str = Field(alias="CharacterName")
    language: str = Field("ja_JP", alias="Language")
    active_after_this_version: Optional[str] = Field(None, alias="ActiveAfterThisVersion")
    voice_file_name: str = Field(alias="VoiceFileName")
    voice_lib_file_name: Optional[str] = Field(None, alias="VoiceLibFileName")
    voice_version: str = Field(alias="VoiceVersion")
    voice_hash: Optional[str] = Field(None, alias="VoiceHash")
    voice_lib_hash: Optional[str] = Field(None, alias="VoiceLibHash")


class VoiSonaGlobalParameter(BaseModel):
    global_vib_amp: float = Field(1, alias="GlobalVibAmp")
    global_vib_frq: float = Field(0, alias="GlobalVibFrq")
    global_alpha: float = Field(0, alias="GlobalAlpha")
    global_husky: float = Field(0, alias="GlobalHusky")
    global_tune: Optional[float] = Field(None, alias="GlobalTune")


class VoiSonaSoundItem(BaseModel):
    clock: int = Field(alias="Clock")
    tempo: float = Field(alias="Tempo")


class VoiSonaTempoItem(BaseModel):
    sound: list[VoiSonaSoundItem] = Field(default_factory=list, alias="Sound")


class VoiSonaTimeItem(BaseModel):
    clock: int = Field(alias="Clock")
    beats: int = Field(alias="Beats")
    beat_type: int = Field(alias="BeatType")


class VoiSonaBeatItem(BaseModel):
    time: list[VoiSonaTimeItem] = Field(default_factory=list, alias="Time")


class VoiSonaKeyItem(BaseModel):
    clock: int = Field(alias="Clock")
    fifths: int = Field(alias="Fifths")
    mode: int = Field(alias="Mode")


class VoiSonaDynamic(BaseModel):
    clock: int = Field(alias="Clock")
    value: int = Field(alias="Value")


class VoiSonaNoteItem(BaseModel):
    clock: int = Field(alias="Clock")
    duration: int = Field(alias="Duration")
    pitch_step: int = Field(alias="PitchStep")
    pitch_octave: int = Field(alias="PitchOctave")
    lyric: str = Field(alias="Lyric")
    syllabic: int = Field(alias="Syllabic")
    phoneme: str = Field(alias="Phoneme")
    do_re_mi: Optional[bool] = Field(None, alias="DoReMi")
    accent: Optional[bool] = Field(None, alias="Accent")
    breath: Optional[bool] = Field(None, alias="Breath")
    staccato: Optional[bool] = Field(None, alias="Staccato")
    slur_start: Optional[bool] = Field(None, alias="SlurStart")
    slur_stop: Optional[bool] = Field(None, alias="SlurStop")


class VoiSonaScoreItem(BaseModel):
    key: list[VoiSonaKeyItem] = Field(default_factory=list, alias="Key")
    dynamics: list[VoiSonaDynamic] = Field(default_factory=list, alias="Dynamics")
    note: list[VoiSonaNoteItem] = Field(default_factory=list, alias="Note")


class VoiSonaSongItem(BaseModel):
    tempo: list[VoiSonaTempoItem] = Field(default_factory=list, alias="Tempo")
    beat: list[VoiSonaBeatItem] = Field(default_factory=list, alias="Beat")
    score: list[VoiSonaScoreItem] = Field(default_factory=list, alias="Score")


class VoiSonaPointData(BaseModel):
    index: Optional[int] = Field(None, alias="Index")
    repeat: Optional[int] = Field(None, alias="Repeat")
    value: float = Field(alias="Value")


class VoiSonaParameterItem(BaseModel):
    length: int = Field(alias="Length")
    data: list[VoiSonaPointData] = Field(default_factory=list, alias="Data")


class VoiSonaParametersItem(BaseModel):
    timing: Optional[list[VoiSonaParameterItem]] = Field(None, alias="Timing")
    c0: Optional[list[VoiSonaParameterItem]] = Field(None, alias="C0")
    c0_c_tick: Optional[list[VoiSonaParameterItem]] = Field(None, alias="C0CTick")
    log_f0: Optional[list[VoiSonaParameterItem]] = Field(None, alias="LogF0")
    log_f0_c_tick: Optional[list[VoiSonaParameterItem]] = Field(None, alias="LogF0CTick")
    vocoder_log_f0: Optional[float] = Field(None, alias="VocoderLogF0")
    vib_amp: Optional[list[VoiSonaParameterItem]] = Field(None, alias="VibAmp")
    vib_amp_c_tick: Optional[list[VoiSonaParameterItem]] = Field(None, alias="VibAmpCTick")
    vib_frq: Optional[list[VoiSonaParameterItem]] = Field(None, alias="VibFrq")
    vib_frq_c_tick: Optional[list[VoiSonaParameterItem]] = Field(None, alias="VibFrqCTick")
    alpha: Optional[list[VoiSonaParameterItem]] = Field(None, alias="Alpha")
    alpha_c_tick: Optional[list[VoiSonaParameterItem]] = Field(None, alias="AlphaCTick")
    husky: Optional[list[VoiSonaParameterItem]] = Field(None, alias="Husky")
    husky_c_tick: Optional[list[VoiSonaParameterItem]] = Field(None, alias="HuskyCTick")


class VoiSonaSignerConfig(BaseModel):
    pass


class VoiSonaStateInformation(BaseModel):
    song_editor: list[VoiSonaSongEditorItem] = Field(default_factory=list, alias="SongEditor")
    control_panel_status: list[VoiSonaControlPanelStatus] = Field(
        default_factory=list, alias="ControlPanelStatus"
    )
    adjust_tool_bar_status: list[VoiSonaAdjustToolBarStatus] = Field(
        default_factory=list, alias="AdjustToolBarStatus"
    )
    main_panel_status: list[VoiSonaMainPanelStatus] = Field(
        default_factory=list, alias="MainPanelStatus"
    )
    panel_controller_status: Optional[list[VoiSonaPanelControllerStatus]] = Field(
        None, alias="PanelControllerStatus"
    )
    voice_information: Optional[list[VoiSonaVoiceInformation]] = Field(
        None, alias="VoiceInformation"
    )
    global_parameters: Optional[list[VoiSonaGlobalParameter]] = Field(
        None, alias="GlobalParameters"
    )
    song: Optional[list[VoiSonaSongItem]] = Field(None, alias="Song")
    parameter: Optional[list[VoiSonaParametersItem]] = Field(None, alias="Parameter")
    tempo_sync: Optional[bool] = Field(False, alias="TempoSync")
    signer_config: Optional[list[VoiSonaSignerConfig]] = Field(None, alias="SignerConfig")
    version_of_app_file_saved: Optional[str] = Field("1.8.0.17", alias="VersionOfAppFileSaved")


class VoiSonaPluginData(BaseModel):
    state_information: VoiSonaStateInformation = Field(
        default_factory=VoiSonaStateInformation, alias="StateInformation"
    )


class VoiSonaAudioEventItem(BaseModel):
    path: str = Field(alias="Path")
    offset: float = Field(alias="Offset")


class VoiSonaTrackType(enum.IntEnum):
    SINGING = 0
    AUDIO = 2


class VoiSonaTrackState(enum.IntEnum):
    NONE = 0
    MUTE = 1
    SOLO = 2


class VoiSonaBaseTrackItem(BaseModel):
    name: str = Field(alias="Name")
    state: VoiSonaTrackState = Field(VoiSonaTrackState.NONE, alias="State")
    volume: float = Field(0, alias="Volume")
    pan: float = Field(0, alias="Pan")


class VoiSonaAudioTrackItem(VoiSonaBaseTrackItem):
    track_type: Literal[VoiSonaTrackType.AUDIO] = Field(VoiSonaTrackType.AUDIO, alias="Type")
    audio_event: Optional[list[VoiSonaAudioEventItem]] = Field(None, alias="AudioEvent")


class VoiSonaSingingTrackItem(VoiSonaBaseTrackItem):
    track_type: Literal[VoiSonaTrackType.SINGING] = Field(VoiSonaTrackType.SINGING, alias="Type")
    plugin_data: VoiSonaPluginData = Field(default_factory=VoiSonaPluginData, alias="PluginData")


VoiSonaTrackItem = Annotated[
    Union[VoiSonaAudioTrackItem, VoiSonaSingingTrackItem],
    Field(discriminator="track_type"),
]


class VoiSonaTrack(BaseModel):
    track: list[VoiSonaTrackItem] = Field(default_factory=list, alias="Track")


class VoiSonaGuiStatus(BaseModel):
    scale_x: float = Field(100, alias="ScaleX")
    scale_y: float = Field(100, alias="ScaleY")
    grid_mode: Optional[int] = Field(None, alias="GridMode")
    grid_index: Optional[int] = Field(None, alias="GridIndex")


class VoiSonaProject(BaseModel):
    play_control: list[VoiSonaPlayControlItem] = Field(default_factory=list, alias="PlayControl")
    tracks: list[VoiSonaTrack] = Field(default_factory=list, alias="Tracks")
    gui_status: list[VoiSonaGuiStatus] = Field(default_factory=list, alias="GUIStatus")
    version_of_app_file_saved: Optional[str] = Field("1.8.0.17", alias="VersionOfAppFileSaved")

    @field_validator("version_of_app_file_saved")
    @classmethod
    def version_validator(cls, value: str, _info: ValidationInfo) -> str:
        if Version(value) < Version("1.8"):
            msg = _("Unsupported project version") + f" {value}"
            raise UnsupportedProjectVersionError(msg)
        return value


def value_to_dict(field_name: str, field_value: Any, field_type: type) -> dict[str, Any]:
    if issubclass(field_type, bool):
        if field_value is True:
            variant_type = JUCEVarTypes.BOOL_TRUE
        elif field_value is False:
            variant_type = JUCEVarTypes.BOOL_FALSE
    elif issubclass(field_type, (enum.IntEnum, int)):
        variant_type = JUCEVarTypes.INT
    elif issubclass(field_type, float):
        variant_type = JUCEVarTypes.DOUBLE
    elif issubclass(field_type, str):
        variant_type = JUCEVarTypes.STRING
    elif issubclass(field_type, bytes):
        variant_type = JUCEVarTypes.BINARY
    else:
        msg = f"Unknown field type {field_type} for field {field_name}"
        raise TypeError(msg)
    return {
        "name": field_name,
        "data": {
            "type": variant_type,
            "value": field_value,
        },
    }


def model_to_value_tree(model: BaseModel, name: str = "TSSolution") -> dict[str, Any]:
    model_class = type(model)
    value_tree = {
        "name": name,
        "attrs": [],
        "children": [],
    }
    for field_name, field_info in model_class.model_fields.items():
        field_value = getattr(model, field_name)
        alias_field_name = field_info.alias or field_name
        if field_value is not None:
            if isinstance(field_info.annotation, type):
                field_type = field_info.annotation
            elif field_info.default is None or field_info.default_factory is list:
                field_type = field_info.annotation
                while not isinstance(field_type, (type, GenericAlias)):
                    field_type = get_args(field_type)[0]
            else:
                field_type = type(field_info.default)
            if isinstance(field_type, GenericAlias):
                inner_type = get_args(field_type)[0]
                if not isinstance(inner_type, type) or issubclass(inner_type, BaseModel):
                    value_tree["children"].extend(
                        model_to_value_tree(item, alias_field_name) for item in field_value
                    )
                else:
                    value_tree["attrs"].extend(
                        value_to_dict(alias_field_name, item, inner_type) for item in field_value
                    )
            elif alias_field_name == "PluginData":
                value_tree["attrs"].append(
                    {
                        "name": alias_field_name,
                        "data": {
                            "type": JUCEVarTypes.BINARY,
                            "value": JUCENode.build(
                                model_to_value_tree(
                                    field_value.state_information,
                                    "StateInformation",
                                )
                            ),
                        },
                    }
                )
            elif issubclass(field_type, BaseModel):
                value_tree["children"].append(model_to_value_tree(field_value, alias_field_name))
            else:
                value_tree["attrs"].append(value_to_dict(alias_field_name, field_value, field_type))
    return value_tree
