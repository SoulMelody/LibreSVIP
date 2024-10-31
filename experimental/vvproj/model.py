from __future__ import annotations

from typing import Optional

from pydantic import Field

from libresvip.model.base import BaseModel


class VoiceVoxVoice(BaseModel):
    engine_id: str = Field(alias="engineId")
    speaker_id: str = Field(alias="speakerId")
    style_id: int = Field(alias="styleId")


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
    is_interrogative: bool = Field(alias="isInterrogative")


class VoiceVoxQuery(BaseModel):
    accent_phrases: list[VoiceVoxAccentPhrase] = Field(alias="accentPhrases")
    speed_scale: int = Field(alias="speedScale")
    pitch_scale: int = Field(alias="pitchScale")
    intonation_scale: int = Field(alias="intonationScale")
    volume_scale: int = Field(alias="volumeScale")
    pre_phoneme_length: float = Field(alias="prePhonemeLength")
    post_phoneme_length: float = Field(alias="postPhonemeLength")
    pause_length_scale: int = Field(alias="pauseLengthScale")
    output_sampling_rate: int = Field(alias="outputSamplingRate")
    output_stereo: bool = Field(alias="outputStereo")
    kana: str


class VoiceVoxAudioItem(BaseModel):
    text: str
    voice: VoiceVoxVoice
    query: VoiceVoxQuery
    preset_key: str = Field(alias="presetKey")


class VoiceVoxTalk(BaseModel):
    audio_keys: list[str] = Field(alias="audioKeys")
    audio_items: dict[str, VoiceVoxAudioItem] = Field(alias="audioItems")


class VoiceVoxTempo(BaseModel):
    position: int
    bpm: int


class VoiceVoxTimeSignature(BaseModel):
    measure_number: int = Field(alias="measureNumber")
    beats: int
    beat_type: int = Field(alias="beatType")


class VoiceVoxSinger(BaseModel):
    engine_id: str = Field(alias="engineId")
    style_id: int = Field(alias="styleId")


class VoiceVoxNote(BaseModel):
    id: str
    position: int
    duration: int
    note_number: int = Field(alias="noteNumber")
    lyric: str


class VoiceVoxTrack(BaseModel):
    name: str
    singer: VoiceVoxSinger
    key_range_adjustment: int = Field(alias="keyRangeAdjustment")
    volume_range_adjustment: int = Field(alias="volumeRangeAdjustment")
    notes: list[VoiceVoxNote]
    pitch_edit_data: list[float] = Field(alias="pitchEditData")
    solo: bool
    mute: bool
    gain: int
    pan: int


class VoiceVoxSong(BaseModel):
    tpqn: int
    tempos: list[VoiceVoxTempo]
    time_signatures: list[VoiceVoxTimeSignature] = Field(alias="timeSignatures")
    tracks: dict[str, VoiceVoxTrack]
    track_order: list[str] = Field(alias="trackOrder")


class VoiceVoxProject(BaseModel):
    app_version: str = Field(alias="appVersion")
    talk: VoiceVoxTalk
    song: VoiceVoxSong
