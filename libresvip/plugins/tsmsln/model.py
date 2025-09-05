# mypy: disable-error-code="attr-defined"
from __future__ import annotations

import enum
from types import GenericAlias
from typing import Any, Literal, get_args

from pydantic import AliasChoices, Field

from libresvip.model.base import BaseModel
from libresvip.utils.binary.value_tree import JUCENode, JUCEVarTypes


class VoiSonaMobilePlayControlItem(BaseModel):
    loop: bool = Field(alias="Loop")
    loop_start: float = Field(0, alias="LoopStart")
    loop_end: float = Field(alias="LoopEnd")
    play_position: float = Field(alias="PlayPosition")


class VoiSonaMobileSongEditorItem(BaseModel):
    editor_width: int = Field(1920, alias="EditorWidth")
    editor_height: int = Field(1080, alias="EditorHeight")


class VoiSonaMobileControlPanelStatus(BaseModel):
    quantization: int = Field(alias="Quantization")
    edit_tool: int | None = Field(None, alias="EditTool")
    record_note: bool = Field(True, alias="RecordNote")
    record_tempo: bool = Field(True, alias="RecordTempo")


class VoiSonaMobileAdjustToolBarStatus(BaseModel):
    main_panel: int = Field(alias="MainPanel")
    sub_panel: int = Field(alias="SubPanel")


class VoiSonaMobilePanelControllerStatus(BaseModel):
    tempo_panel: bool | None = Field(None, alias="TempoPanel")
    beat_panel: bool | None = Field(None, alias="BeatPanel")
    key_panel: bool | None = Field(None, alias="KeyPanel")
    dynamics_panel: bool | None = Field(None, alias="DynamicsPanel")
    global_param_panel: bool | None = Field(None, alias="GlobalParamPanel")
    lyric_panel: bool | None = Field(None, alias="LyricPanel")
    property_panel: bool | None = Field(None, alias="PropertyPanel")


class VoiSonaMobileMainPanelStatus(VoiSonaMobilePanelControllerStatus):
    scale_x: float = Field(alias="ScaleX_V2", validation_alias=AliasChoices("ScaleX_V2", "ScaleX"))
    scale_y: float = Field(alias="ScaleY_V2", validation_alias=AliasChoices("ScaleY_V2", "ScaleY"))
    scroll_x: float | None = Field(None, alias="ScrollX")
    scroll_y: float | None = Field(None, alias="ScrollY")


class VoiSonaMobileNeuralVocoderInformation(BaseModel):
    nv_file_name: str = Field(alias="NVFileName")
    nv_lib_file_name: str | None = Field(None, alias="NVLibFileName")
    nv_version: str = Field(alias="NVVersion")
    nv_hash: str | None = Field(None, alias="NVHash")
    nv_lib_hash: str | None = Field(None, alias="NVLibHash")
    nv_label: str = Field(alias="NVLabel")


class VoiSonaMobileNeuralVocoderListItem(BaseModel):
    neural_vocoder_information: list[VoiSonaMobileNeuralVocoderInformation] | None = Field(
        None, alias="NeuralVocoderInformation"
    )


class VoiSonaMobileEmotionItem(BaseModel):
    label: str = Field(alias="Label")
    ratio: float = Field(alias="Ratio")


class VoiSonaMobileEmotionListItem(BaseModel):
    emotion: list[VoiSonaMobileEmotionItem] = Field(default_factory=list, alias="Emotion")


class VoiSonaMobileSpecialSymbol(BaseModel):
    special_symbol_raspy: list[str] = Field(default_factory=list, alias="SpecialSymbolRaspy")
    special_symbol_falsetto: list[str] = Field(default_factory=list, alias="SpecialSymbolFalsetto")


class VoiSonaMobileVoiceInformation(BaseModel):
    neural_vocoder_list: list[VoiSonaMobileNeuralVocoderListItem] = Field(
        default_factory=list, alias="NeuralVocoderList"
    )
    emotion_list: list[VoiSonaMobileEmotionListItem] = Field(
        default_factory=list, alias="EmotionList"
    )
    character_name: str = Field(alias="CharacterName")
    language: str = Field("ja_JP", alias="Language")
    active_after_this_version: str | None = Field(None, alias="ActiveAfterThisVersion")
    voice_file_name: str = Field(alias="VoiceFileName")
    voice_lib_file_name: str | None = Field(None, alias="VoiceLibFileName")
    voice_version: str = Field(alias="VoiceVersion")
    voice_hash: str | None = Field(None, alias="VoiceHash")
    voice_lib_hash: str | None = Field(None, alias="VoiceLibHash")
    special_symbol: list[VoiSonaMobileSpecialSymbol] = Field(
        default_factory=list, alias="SpecialSymbol"
    )


class VoiSonaMobileGlobalParameter(BaseModel):
    global_vib_amp: float = Field(1, alias="GlobalVibAmp")
    global_vib_frq: float = Field(0, alias="GlobalVibFrq")
    global_alpha: float = Field(0, alias="GlobalAlpha")
    global_husky: float = Field(0, alias="GlobalHusky")
    global_tune: float | None = Field(None, alias="GlobalTune")


class VoiSonaMobileSoundItem(BaseModel):
    clock: int = Field(alias="Clock")
    tempo: float = Field(alias="Tempo")


class VoiSonaMobileTempoItem(BaseModel):
    sound: list[VoiSonaMobileSoundItem] = Field(default_factory=list, alias="Sound")


class VoiSonaMobileTimeItem(BaseModel):
    clock: int = Field(alias="Clock")
    beats: int = Field(alias="Beats")
    beat_type: int = Field(alias="BeatType")


class VoiSonaMobileBeatItem(BaseModel):
    time: list[VoiSonaMobileTimeItem] = Field(default_factory=list, alias="Time")


class VoiSonaMobileKeyItem(BaseModel):
    clock: int = Field(alias="Clock")
    fifths: int = Field(alias="Fifths")
    mode: int = Field(alias="Mode")


class VoiSonaMobileDynamic(BaseModel):
    clock: int = Field(alias="Clock")
    value: int = Field(alias="Value")


class VoiSonaMobileNoteItem(BaseModel):
    clock: int = Field(alias="Clock")
    duration: int = Field(alias="Duration")
    pitch_step: int = Field(alias="PitchStep")
    pitch_octave: int = Field(alias="PitchOctave")
    lyric: str = Field(alias="Lyric")
    syllabic: int = Field(alias="Syllabic")
    phoneme: str = Field(alias="Phoneme")
    do_re_mi: bool | None = Field(None, alias="DoReMi")
    accent: bool | None = Field(None, alias="Accent")
    breath: bool | None = Field(None, alias="Breath")
    staccato: bool | None = Field(None, alias="Staccato")
    slur_start: bool | None = Field(None, alias="SlurStart")
    slur_stop: bool | None = Field(None, alias="SlurStop")
    default_phoneme: str | None = Field(None, alias="DefaultPhoneme")
    past_analyzed_phoneme: str | None = Field(None, alias="PastAnalyzedPhoneme")
    special_symbol_raspy: bool | None = Field(None, alias="SpecialSymbolRaspy")
    special_symbol_falsetto: bool | None = Field(None, alias="SpecialSymbolFalsetto")


class VoiSonaMobileScoreItem(BaseModel):
    key: list[VoiSonaMobileKeyItem] = Field(default_factory=list, alias="Key")
    dynamics: list[VoiSonaMobileDynamic] = Field(default_factory=list, alias="Dynamics")
    note: list[VoiSonaMobileNoteItem] = Field(default_factory=list, alias="Note")


class VoiSonaMobileSongItem(BaseModel):
    tempo: list[VoiSonaMobileTempoItem] = Field(default_factory=list, alias="Tempo")
    beat: list[VoiSonaMobileBeatItem] = Field(default_factory=list, alias="Beat")
    score: list[VoiSonaMobileScoreItem] = Field(default_factory=list, alias="Score")


class VoiSonaMobilePointData(BaseModel):
    index: int | None = Field(None, alias="Index")
    repeat: int | None = Field(None, alias="Repeat")
    value: float = Field(alias="Value")


class VoiSonaMobileParameterItem(BaseModel):
    length: int = Field(alias="Length")
    data: list[VoiSonaMobilePointData] = Field(default_factory=list, alias="Data")


class VoiSonaMobileParametersItem(BaseModel):
    timing: list[VoiSonaMobileParameterItem] | None = Field(None, alias="Timing")
    c0: list[VoiSonaMobileParameterItem] | None = Field(None, alias="C0")
    c0_c_tick: list[VoiSonaMobileParameterItem] | None = Field(None, alias="C0CTick")
    log_f0: list[VoiSonaMobileParameterItem] | None = Field(None, alias="LogF0")
    log_f0_c_tick: list[VoiSonaMobileParameterItem] | None = Field(None, alias="LogF0CTick")
    vocoder_log_f0: float | None = Field(None, alias="VocoderLogF0")
    vib_amp: list[VoiSonaMobileParameterItem] | None = Field(None, alias="VibAmp")
    vib_amp_c_tick: list[VoiSonaMobileParameterItem] | None = Field(None, alias="VibAmpCTick")
    vib_frq: list[VoiSonaMobileParameterItem] | None = Field(None, alias="VibFrq")
    vib_frq_c_tick: list[VoiSonaMobileParameterItem] | None = Field(None, alias="VibFrqCTick")
    alpha: list[VoiSonaMobileParameterItem] | None = Field(None, alias="Alpha")
    alpha_c_tick: list[VoiSonaMobileParameterItem] | None = Field(None, alias="AlphaCTick")
    husky: list[VoiSonaMobileParameterItem] | None = Field(None, alias="Husky")
    husky_c_tick: list[VoiSonaMobileParameterItem] | None = Field(None, alias="HuskyCTick")


class VoiSonaMobileSignerConfig(BaseModel):
    snap_shot: str | None = Field(None, alias="SnapShot")


class VoiSonaMobileStateInformation(BaseModel):
    song_editor: list[VoiSonaMobileSongEditorItem] = Field(default_factory=list, alias="SongEditor")
    control_panel_status: list[VoiSonaMobileControlPanelStatus] = Field(
        default_factory=list, alias="ControlPanelStatus"
    )
    adjust_tool_bar_status: list[VoiSonaMobileAdjustToolBarStatus] = Field(
        default_factory=list, alias="AdjustToolBarStatus"
    )
    main_panel_status: list[VoiSonaMobileMainPanelStatus] = Field(
        default_factory=list, alias="MainPanelStatus"
    )
    panel_controller_status: list[VoiSonaMobilePanelControllerStatus] | None = Field(
        None, alias="PanelControllerStatus"
    )
    voice_information: list[VoiSonaMobileVoiceInformation] | None = Field(
        None, alias="VoiceInformation"
    )
    global_parameters: list[VoiSonaMobileGlobalParameter] | None = Field(
        None, alias="GlobalParameters"
    )
    song: list[VoiSonaMobileSongItem] | None = Field(None, alias="Song")
    parameter: list[VoiSonaMobileParametersItem] | None = Field(None, alias="Parameter")
    tempo_sync: bool | None = Field(False, alias="TempoSync")
    signer_config: list[VoiSonaMobileSignerConfig] | None = Field(None, alias="SignerConfig")
    version_of_app_file_saved: str | None = Field("1.12.1.0", alias="VersionOfAppFileSaved")


class VoiSonaPluginData(BaseModel):
    state_information: VoiSonaMobileStateInformation = Field(
        default_factory=VoiSonaMobileStateInformation, alias="StateInformation"
    )


class VoiSonaMobileTrackType(enum.IntEnum):
    SINGING = 0


class VoiSonaMobileBaseTrackItem(BaseModel):
    name: str = Field(alias="Name")
    state: int = Field(0, alias="State")
    volume: float = Field(0, alias="Volume")
    pan: float = Field(0, alias="Pan")


class VoiSonaMobileSingingTrackItem(VoiSonaMobileBaseTrackItem):
    track_type: Literal[VoiSonaMobileTrackType.SINGING] = Field(
        VoiSonaMobileTrackType.SINGING, alias="Type"
    )
    plugin_data: VoiSonaPluginData = Field(default_factory=VoiSonaPluginData, alias="PluginData")


class VoiSonaMobileTrack(BaseModel):
    track: list[VoiSonaMobileSingingTrackItem] = Field(default_factory=list, alias="Track")


class VoiSonaMobileSingerData(BaseModel):
    state_information: VoiSonaMobileStateInformation = Field(
        default_factory=VoiSonaMobileStateInformation, alias="StateInformation"
    )


class VoiSonaMobileSinger(BaseModel):
    mobile_singer_data: VoiSonaMobileSingerData = Field(
        default_factory=VoiSonaMobileSingerData, alias="ModileSingerData"
    )


class VoiSonaMobileAudio(BaseModel):
    mobile_offset: int = Field(0, alias="ModileOffset")
    mobile_volume: float = Field(0, alias="ModileVolume")
    mobile_audio_data: str = Field(alias="ModileAudioData")


class VoiSonaMobileProject(BaseModel):
    tracks: list[VoiSonaMobileTrack] = Field(default_factory=list, alias="Tracks")
    version_of_app_file_saved: str | None = Field("1.12.1.0", alias="VersionOfAppFileSaved")
    mobile_singer: list[VoiSonaMobileSinger] = Field(default_factory=list, alias="MobileSinger")
    mobile_audio: list[VoiSonaMobileAudio] = Field(default_factory=list, alias="MobileAudio")


def value_to_dict(field_value: Any, field_type: type) -> dict[str, Any]:
    if issubclass(field_type, bool):
        variant_type = JUCEVarTypes.BOOL_TRUE if field_value is True else JUCEVarTypes.BOOL_FALSE
    elif issubclass(field_type, enum.IntEnum | int):
        variant_type = JUCEVarTypes.INT
    elif issubclass(field_type, float):
        variant_type = JUCEVarTypes.DOUBLE
    elif issubclass(field_type, str):
        variant_type = JUCEVarTypes.STRING
    elif issubclass(field_type, bytes):
        variant_type = JUCEVarTypes.BINARY
    elif issubclass(field_type, list):
        variant_type = JUCEVarTypes.ARRAY
        field_value = [value_to_dict(item, type(item)) for item in field_value]
    else:
        variant_type = None
        msg = f"Unknown field type {field_type}"
        raise TypeError(msg)
    return {
        "type": variant_type,
        "value": field_value,
    }


def model_to_value_tree(model: BaseModel, name: str = "MobileSongEditor") -> dict[str, Any]:
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
                while not isinstance(field_type, type | GenericAlias):
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
                        {"name": alias_field_name, "data": value_to_dict(item, inner_type)}
                        for item in field_value
                    )
            elif alias_field_name == "ModileSingerData":
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
                value_tree["attrs"].append(
                    {"name": alias_field_name, "data": value_to_dict(field_value, field_type)}
                )
    return value_tree
