from __future__ import annotations

from typing import Optional

from pydantic import Field

from libresvip.core.constants import TICKS_IN_BEAT
from libresvip.model.base import BaseModel
from libresvip.utils.text import uuid_str


class VoiceVoxSinger(BaseModel):
    engine_id: str = Field("074fc39e-678b-4c13-8916-ffca8d505d1d", alias="engineId")
    style_id: int = Field(3002, alias="styleId")


class VoiceVoxVoice(VoiceVoxSinger):
    speaker_id: str = Field("7ffcb7ce-00ec-4bdc-82cd-45a8889e43ff", alias="speakerId")
    style_id: int = Field(2, alias="styleId")


class VoiceVoxMora(BaseModel):
    text: str
    vowel: str
    vowel_length: float = Field(alias="vowelLength")
    pitch: float
    consonant: Optional[str] = None
    consonant_length: Optional[float] = Field(None, alias="consonantLength")


class VoiceVoxAccentPhrase(BaseModel):
    moras: list[VoiceVoxMora]
    accent: int
    mora: Optional[VoiceVoxMora] = None
    is_interrogative: bool = Field(alias="isInterrogative")


class VoiceVoxQuery(BaseModel):
    accent_phrases: list[VoiceVoxAccentPhrase] = Field(alias="accentPhrases")
    speed_scale: float = Field(alias="speedScale")
    pitch_scale: float = Field(alias="pitchScale")
    intonation_scale: float = Field(alias="intonationScale")
    volume_scale: float = Field(alias="volumeScale")
    pre_phoneme_length: float = Field(alias="prePhonemeLength")
    post_phoneme_length: float = Field(alias="postPhonemeLength")
    pause_length: Optional[float] = Field(None, alias="pauseLength")
    pause_length_scale: float = Field(1, alias="pauseLengthScale")
    output_sampling_rate: int = Field(alias="outputSamplingRate")
    output_stereo: bool = Field(alias="outputStereo")
    kana: Optional[str] = None


class VoiceVoxAudioItem(BaseModel):
    text: str
    voice: VoiceVoxVoice
    query: VoiceVoxQuery
    preset_key: str = Field(default_factory=uuid_str, alias="presetKey")


class VoiceVoxTalk(BaseModel):
    audio_keys: list[str] = Field(default_factory=list, alias="audioKeys")
    audio_items: dict[str, VoiceVoxAudioItem] = Field(default_factory=dict, alias="audioItems")


class VoiceVoxTempo(BaseModel):
    position: int
    bpm: int


class VoiceVoxTimeSignature(BaseModel):
    measure_number: int = Field(alias="measureNumber")
    beats: int
    beat_type: int = Field(alias="beatType")


class VoiceVoxNote(BaseModel):
    id: str = Field(default_factory=uuid_str)
    position: int
    duration: int
    note_number: int = Field(alias="noteNumber")
    lyric: str


class VoiceVoxTrack(BaseModel):
    name: str
    singer: VoiceVoxSinger = Field(default_factory=VoiceVoxSinger)
    key_range_adjustment: int = Field(0, alias="keyRangeAdjustment")
    volume_range_adjustment: int = Field(0, alias="volumeRangeAdjustment")
    notes: list[VoiceVoxNote] = Field(default_factory=list)
    pitch_edit_data: list[float] = Field(alias="pitchEditData", default_factory=list)
    solo: bool = False
    mute: bool = False
    gain: float = 1.0
    pan: float = 0.0


class VoiceVoxSong(BaseModel):
    tpqn: int = TICKS_IN_BEAT
    tempos: list[VoiceVoxTempo] = Field(default_factory=list)
    time_signatures: list[VoiceVoxTimeSignature] = Field(
        alias="timeSignatures", default_factory=list
    )
    tracks: dict[str, VoiceVoxTrack] = Field(default_factory=dict)
    track_order: list[str] = Field(alias="trackOrder", default_factory=list)


class VoiceVoxProject(BaseModel):
    app_version: str = Field("0.21.1", alias="appVersion")
    talk: VoiceVoxTalk = Field(default_factory=VoiceVoxTalk)
    song: VoiceVoxSong = Field(default_factory=VoiceVoxSong)
