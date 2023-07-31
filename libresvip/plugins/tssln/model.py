from __future__ import annotations

import enum
from typing import Annotated, Literal, Optional, Union

from pydantic import Field

from libresvip.model.base import BaseModel


class VoiSonaPlayControlItem(BaseModel):
    loop: bool = Field(alias="Loop")
    loop_start: float = Field(alias="LoopStart")
    loop_end: float = Field(alias="LoopEnd")
    play_position: float = Field(alias="PlayPosition")


class VoiSonaSongEditorItem(BaseModel):
    editor_width: int = Field(alias="EditorWidth")
    editor_height: int = Field(alias="EditorHeight")


class VoiSonaControlPanelStatus(BaseModel):
    quantization: int = Field(alias="Quantization")
    edit_tool: Optional[int] = Field(None, alias="EditTool")
    record_note: bool = Field(alias="RecordNote")
    record_tempo: bool = Field(alias="RecordTempo")


class VoiSonaAdjustToolBarStatus(BaseModel):
    main_panel: int = Field(alias="MainPanel")
    sub_panel: int = Field(alias="SubPanel")


class VoiSonaPanelControllerStatus(BaseModel):
    tempo_panel: Optional[bool] = Field(None, alias="TempoPanel")
    beat_panel: Optional[bool] = Field(None, alias="BeatPanel")
    key_panel: Optional[bool] = Field(None, alias="KeyPanel")


class VoiSonaMainPanelStatus(BaseModel):
    scale_x: float = Field(alias="ScaleX")
    scale_y: float = Field(alias="ScaleY")
    scroll_x: Optional[float] = Field(None, alias="ScrollX")
    scroll_y: Optional[float] = Field(None, alias="ScrollY")
    tempo_panel: Optional[bool] = Field(None, alias="TempoPanel")
    beat_panel: Optional[bool] = Field(None, alias="BeatPanel")
    key_panel: Optional[bool] = Field(None, alias="KeyPanel")


class VoiSonaNeuralVocoderInformation(BaseModel):
    nv_file_name: str = Field(alias="NVFileName")
    nv_lib_file_name: Optional[str] = Field(None, alias="NVLibFileName")
    nv_version: str = Field(alias="NVVersion")
    nv_hash: Optional[str] = Field(None, alias="NVHash")
    nv_lib_hash: Optional[str] = Field(None, alias="NVLibHash")
    nv_label: str = Field(alias="NVLabel")


class VoiSonaNeuralVocoderListItem(BaseModel):
    neural_vocoder_information: list[VoiSonaNeuralVocoderInformation] = Field(
        alias="NeuralVocoderInformation"
    )


class VoiSonaEmotionItem(BaseModel):
    label: str = Field(alias="Label")
    ratio: float = Field(alias="Ratio")


class VoiSonaEmotionListItem(BaseModel):
    emotion: list[VoiSonaEmotionItem] = Field(alias="Emotion")


class VoiSonaVoiceInformation(BaseModel):
    neural_vocoder_list: list[VoiSonaNeuralVocoderListItem] = Field(
        alias="NeuralVocoderList"
    )
    emotion_list: list[VoiSonaEmotionListItem] = Field(alias="EmotionList")
    character_name: str = Field(alias="CharacterName")
    language: str = Field(alias="Language")
    active_after_this_version: Optional[str] = Field(
        None, alias="ActiveAfterThisVersion"
    )
    voice_file_name: str = Field(alias="VoiceFileName")
    voice_lib_file_name: Optional[str] = Field(None, alias="VoiceLibFileName")
    voice_version: str = Field(alias="VoiceVersion")
    voice_hash: Optional[str] = Field(None, alias="VoiceHash")
    voice_lib_hash: Optional[str] = Field(None, alias="VoiceLibHash")


class VoiSonaGlobalParameter(BaseModel):
    global_vib_amp: float = Field(alias="GlobalVibAmp")
    global_vib_frq: float = Field(alias="GlobalVibFrq")
    global_alpha: float = Field(alias="GlobalAlpha")
    global_husky: float = Field(alias="GlobalHusky")
    global_tune: Optional[float] = Field(None, alias="GlobalTune")


class VoiSonaSoundItem(BaseModel):
    clock: int = Field(alias="Clock")
    tempo: float = Field(alias="Tempo")


class VoiSonaTempoItem(BaseModel):
    sound: list[VoiSonaSoundItem] = Field(alias="Sound")


class VoiSonaTimeItem(BaseModel):
    clock: int = Field(alias="Clock")
    beats: int = Field(alias="Beats")
    beat_type: int = Field(alias="BeatType")


class VoiSonaBeatItem(BaseModel):
    time: list[VoiSonaTimeItem] = Field(alias="Time")


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


class VoiSonaScoreItem(BaseModel):
    key: list[VoiSonaKeyItem] = Field(alias="Key")
    dynamics: list[VoiSonaDynamic] = Field(alias="Dynamics")
    note: list[VoiSonaNoteItem] = Field(alias="Note")


class VoiSonaSongItem(BaseModel):
    tempo: list[VoiSonaTempoItem] = Field(alias="Tempo")
    beat: list[VoiSonaBeatItem] = Field(alias="Beat")
    score: list[VoiSonaScoreItem] = Field(alias="Score")


class VoiSonaPointData(BaseModel):
    index: Optional[int] = Field(None, alias="Index")
    repeat: Optional[int] = Field(None, alias="Repeat")
    value: float = Field(alias="Value")


class VoiSonaParameterItem(BaseModel):
    data: list[VoiSonaPointData] = Field(alias="Data")
    length: int = Field(alias="Length")


class VoiSonaParametersItem(BaseModel):
    timing: Optional[list[VoiSonaParameterItem]] = Field(None, alias="Timing")
    c0: Optional[list[VoiSonaParameterItem]] = Field(None, alias="C0")
    log_f0: Optional[list[VoiSonaParameterItem]] = Field(None, alias="LogF0")
    vocoder_log_f0: Optional[float] = Field(None, alias="VocoderLogF0")
    vib_amp: Optional[list[VoiSonaParameterItem]] = Field(None, alias="VibAmp")
    alpha: Optional[list[VoiSonaParameterItem]] = Field(None, alias="Alpha")
    alpha_c_tick: Optional[list[VoiSonaParameterItem]] = Field(None, alias="AlphaCTick")
    husky: Optional[list[VoiSonaParameterItem]] = Field(None, alias="Husky")
    husky_c_tick: Optional[list[VoiSonaParameterItem]] = Field(None, alias="HuskyCTick")


class VoiSonaSignerConfig(BaseModel):
    pass


class VoiSonaStateInformation(BaseModel):
    song_editor: list[VoiSonaSongEditorItem] = Field(alias="SongEditor")
    control_panel_status: list[VoiSonaControlPanelStatus] = Field(
        alias="ControlPanelStatus"
    )
    adjust_tool_bar_status: list[VoiSonaAdjustToolBarStatus] = Field(
        alias="AdjustToolBarStatus"
    )
    main_panel_status: list[VoiSonaMainPanelStatus] = Field(alias="MainPanelStatus")
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
    tempo_sync: Optional[bool] = Field(None, alias="TempoSync")
    signer_config: Optional[list[VoiSonaSignerConfig]] = Field(
        None, alias="SignerConfig"
    )


class VoiSonaPluginData(BaseModel):
    state_information: VoiSonaStateInformation = Field(alias="StateInformation")


class VoiSonaAudioEventItem(BaseModel):
    path: str = Field(..., alias="Path")
    offset: float = Field(..., alias="Offset")


class VoiSonaTrackType(enum.IntEnum):
    SINGING = 0
    AUDIO = 2


class VoiSonaTrackState(enum.IntEnum):
    NONE = 0
    MUTE = 1
    SOLO = 2


class VoiSonaBaseTrackItem(BaseModel):
    name: str = Field(alias="Name")
    state: VoiSonaTrackState = Field(alias="State")
    volume: float = Field(alias="Volume")
    pan: float = Field(alias="Pan")


class VoiSonaAudioTrackItem(VoiSonaBaseTrackItem):
    track_type: Literal[VoiSonaTrackType.AUDIO] = Field(
        VoiSonaTrackType.AUDIO, alias="Type"
    )
    audio_event: list[VoiSonaAudioEventItem] = Field(alias="AudioEvent")


class VoiSonaSingingTrackItem(VoiSonaBaseTrackItem):
    track_type: Literal[VoiSonaTrackType.SINGING] = Field(
        VoiSonaTrackType.SINGING, alias="Type"
    )
    plugin_data: VoiSonaPluginData = Field(alias="PluginData")


VoiSonaTrackItem = Annotated[
    Union[VoiSonaAudioTrackItem, VoiSonaSingingTrackItem],
    Field(discriminator="track_type"),
]


class VoiSonaTrack(BaseModel):
    track: list[VoiSonaTrackItem] = Field(alias="Track")


class VoiSonaGuiStatus(BaseModel):
    scale_x: float = Field(alias="ScaleX")
    scale_y: float = Field(alias="ScaleY")
    grid_index: Optional[int] = Field(None, alias="GridIndex")


class VoiSonaProject(BaseModel):
    play_control: list[VoiSonaPlayControlItem] = Field(alias="PlayControl")
    tracks: list[VoiSonaTrack] = Field(alias="Tracks")
    gui_status: list[VoiSonaGuiStatus] = Field(alias="GUIStatus")
