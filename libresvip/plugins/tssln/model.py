from __future__ import annotations

import enum
from typing import Annotated, Literal, Optional, Union

from pydantic import BaseModel, Field


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
    record_note: bool = Field(alias="RecordNote")
    record_tempo: bool = Field(alias="RecordTempo")


class VoiSonaAdjustToolBarStatus(BaseModel):
    main_panel: int = Field(alias="MainPanel")
    sub_panel: int = Field(alias="SubPanel")


class VoiSonaMainPanelStatus(BaseModel):
    scale_x: float = Field(alias="ScaleX")
    scale_y: float = Field(alias="ScaleY")
    tempo_panel: Optional[bool] = Field(None, alias="TempoPanel")
    beat_panel: Optional[bool] = Field(None, alias="BeatPanel")
    key_panel: Optional[bool] = Field(None, alias="KeyPanel")


class VoiSonaNeuralVocoderInformation(BaseModel):
    nv_file_name: str = Field(alias="NVFileName")
    nv_lib_file_name: str = Field(alias="NVLibFileName")
    nv_version: str = Field(alias="NVVersion")
    nv_hash: str = Field(alias="NVHash")
    nv_lib_hash: str = Field(alias="NVLibHash")
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
    voice_file_name: str = Field(alias="VoiceFileName")
    voice_lib_file_name: str = Field(alias="VoiceLibFileName")
    language: str = Field(alias="Language")
    voice_version: str = Field(alias="VoiceVersion")
    voice_hash: str = Field(alias="VoiceHash")
    voice_lib_hash: str = Field(alias="VoiceLibHash")


class VoiSonaGlobalParameter(BaseModel):
    global_vib_amp: float = Field(alias="GlobalVibAmp")
    global_vib_frq: float = Field(alias="GlobalVibFrq")
    global_alpha: float = Field(alias="GlobalAlpha")
    global_husky: float = Field(alias="GlobalHusky")


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


class VoiSonaScoreItem(BaseModel):
    key: list[VoiSonaKeyItem] = Field(alias="Key")
    dynamics: list[VoiSonaDynamic] = Field(alias="Dynamics")
    note: list[VoiSonaNoteItem] = Field(alias="Note")


class VoiSonaSongItem(BaseModel):
    tempo: list[VoiSonaTempoItem] = Field(alias="Tempo")
    beat: list[VoiSonaBeatItem] = Field(alias="Beat")
    score: list[VoiSonaScoreItem] = Field(alias="Score")


class VoiSonaTimingItem(BaseModel):
    data: list[VoiSonaPointData] = Field(alias="Data")
    length: int = Field(alias="Length")


class VoiSonaPointData(BaseModel):
    index: Optional[int] = Field(None, alias="Index")
    repeat: Optional[int] = Field(None, alias="Repeat")
    value: float = Field(alias="Value")


class VoiSonaC0Item(BaseModel):
    data: list[VoiSonaPointData] = Field(alias="Data")
    length: int = Field(alias="Length")


class VoiSonaLogF0Item(BaseModel):
    data: list[VoiSonaPointData] = Field(alias="Data")
    length: int = Field(alias="Length")


class VoiSonaVibAmpItem(BaseModel):
    data: list[VoiSonaPointData] = Field(alias="Data")
    length: int = Field(alias="Length")


class VoiSonaParameterItem(BaseModel):
    timing: list[VoiSonaTimingItem] = Field(alias="Timing")
    c0: list[VoiSonaC0Item] = Field(alias="C0")
    log_f0: list[VoiSonaLogF0Item] = Field(alias="LogF0")
    vib_amp: list[VoiSonaVibAmpItem] = Field(alias="VibAmp")


class VoiSonaStateInformation(BaseModel):
    song_editor: list[VoiSonaSongEditorItem] = Field(alias="SongEditor")
    control_panel_status: list[VoiSonaControlPanelStatus] = Field(
        alias="ControlPanelStatus"
    )
    adjust_tool_bar_status: list[VoiSonaAdjustToolBarStatus] = Field(
        alias="AdjustToolBarStatus"
    )
    main_panel_status: list[VoiSonaMainPanelStatus] = Field(alias="MainPanelStatus")
    voice_information: Optional[list[VoiSonaVoiceInformation]] = Field(
        None, alias="VoiceInformation"
    )
    global_parameters: Optional[list[VoiSonaGlobalParameter]] = Field(
        None, alias="GlobalParameters"
    )
    song: Optional[list[VoiSonaSongItem]] = Field(None, alias="Song")
    parameter: Optional[list[VoiSonaParameterItem]] = Field(None, alias="Parameter")


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


class VoiSonaProject(BaseModel):
    play_control: list[VoiSonaPlayControlItem] = Field(alias="PlayControl")
    tracks: list[VoiSonaTrack] = Field(alias="Tracks")
    gui_status: list[VoiSonaGuiStatus] = Field(alias="GUIStatus")
