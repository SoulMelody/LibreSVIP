import dataclasses
import functools
import math
import pathlib
import secrets

import more_itertools
import portion

from libresvip.core.constants import DEFAULT_BPM, DEFAULT_PHONEME, TICKS_IN_BEAT
from libresvip.core.time_interval import PiecewiseIntervalDict
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import (
    InstrumentalTrack,
    Note,
    ParamCurve,
    Params,
    Project,
    SongTempo,
    TimeSignature,
    Track,
)
from libresvip.utils.audio import audio_track_info
from libresvip.utils.music_math import linear_interpolation

from .model import (
    VOXFactoryAudioClip,
    VOXFactoryAudioData,
    VOXFactoryAudioTrack,
    VOXFactoryNote,
    VOXFactoryProject,
    VOXFactoryTrack,
    VOXFactoryVocalClip,
    VOXFactoryVocalTrack,
)
from .options import OutputOptions


@dataclasses.dataclass
class VOXFactoryGenerator:
    options: OutputOptions
    prefix: str = dataclasses.field(init=False)
    audio_paths: dict[str, pathlib.Path] = dataclasses.field(default_factory=dict)
    synchronizer: TimeSynchronizer = dataclasses.field(init=False)
    first_bar_length: int = dataclasses.field(init=False)

    def generate_project(self, project: Project) -> VOXFactoryProject:
        self.prefix = secrets.token_hex(5)
        self.first_bar_length = int(project.time_signature_list[0].bar_length())
        self.synchronizer = TimeSynchronizer(project.song_tempo_list)
        track_bank, audio_data_bank = self.generate_tracks(project.track_list)
        return VOXFactoryProject(
            tempo=self.generate_tempo(project.song_tempo_list),
            time_signature=self.generate_time_signature(project.time_signature_list),
            track_bank=track_bank,
            track_order=sorted(track_bank.keys()),
            audio_data_bank=audio_data_bank,
        )

    def generate_tempo(self, tempos: list[SongTempo]) -> float:
        return tempos[0].bpm if tempos else DEFAULT_BPM

    def generate_time_signature(self, time_signatures: list[TimeSignature]) -> list[int]:
        if time_signatures:
            return [time_signatures[0].numerator, time_signatures[0].denominator]
        else:
            return [4, 4]

    def generate_tracks(
        self, tracks: list[Track]
    ) -> tuple[dict[str, VOXFactoryTrack], dict[str, VOXFactoryAudioData]]:
        track_bank = {}
        audio_data_bank = {}
        for i, track in enumerate(tracks):
            if isinstance(track, InstrumentalTrack):
                audio_path = pathlib.Path(track.audio_file_path)
                if (track_info := audio_track_info(track.audio_file_path)) is not None:
                    source_audio_data_key = f"{self.prefix}-au{i}{audio_path.suffix}"
                    self.audio_paths[source_audio_data_key] = audio_path
                    audio_data_bank[source_audio_data_key] = VOXFactoryAudioData(
                        sample_rate=44100,
                        sample_length=int(track_info.duration * 44100 / 1000),
                        number_of_channels=track_info.channel_s,
                    )
                    clip_bank = {
                        f"{self.prefix}-cl0": VOXFactoryAudioClip(
                            name=audio_path.stem,
                            offset_quarter=0,
                            start_quarter=track.offset / TICKS_IN_BEAT,
                            length=track_info.duration / 1000,
                            source_audio_data_key=source_audio_data_key,
                        )
                    }
                    clip_order = [f"{self.prefix}-cl0"]
                    track_bank[f"{self.prefix}-tr{i}"] = VOXFactoryAudioTrack(
                        clip_bank=clip_bank,
                        clip_order=clip_order,
                        name=track.title,
                        mute=track.mute,
                        solo=track.solo,
                        pan=track.pan,
                    )
            else:
                clip_bank = self.generate_notes(track.note_list, track.edited_params)
                clip_order = sorted(clip_bank.keys())
                track_bank[f"{self.prefix}-tr{i}"] = VOXFactoryVocalTrack(
                    clip_bank=clip_bank,
                    clip_order=clip_order,
                    name=track.title,
                    mute=track.mute,
                    solo=track.solo,
                    pan=track.pan,
                )
        return track_bank, audio_data_bank

    def generate_notes(self, notes: list[Note], params: Params) -> dict[str, VOXFactoryVocalClip]:
        note_bank = {}
        note_order = []
        max_ticks = notes[-1].end_pos if notes else 0
        max_quarter = max_ticks / TICKS_IN_BEAT
        for i, note in enumerate(notes):
            note_bank[f"{self.prefix}-no{i}"] = self.generate_note(note, params)
            note_order.append(f"{self.prefix}-no{i}")
        clip_count = math.ceil(max_quarter / 32)
        clip_bank = {}
        for i in range(clip_count):
            clip_bank[f"{self.prefix}-cl{i}"] = VOXFactoryVocalClip(
                start_quarter=32 * i,
                offset_quarter=32 * i,
                length=32,
                note_bank=note_bank,
                note_order=note_order,
            )
        return clip_bank

    def generate_note(self, note: Note, params: Params) -> VOXFactoryNote:
        note_start_time = self.synchronizer.get_actual_secs_from_ticks(note.start_pos)
        return VOXFactoryNote(
            time=note_start_time,
            ticks=note.start_pos,
            duration_ticks=note.length,
            midi=note.key_number,
            name=note.lyric,
            syllable=note.pronunciation or DEFAULT_PHONEME,
            pitch_bends=self.generate_note_pitch(note, params.pitch),
        )

    def generate_note_pitch(self, note: Note, pitch: ParamCurve) -> list[float]:
        note_start_time = self.synchronizer.get_actual_secs_from_ticks(note.start_pos)
        note_end_time = self.synchronizer.get_actual_secs_from_ticks(note.end_pos)
        key_interval_dict = PiecewiseIntervalDict()
        secs_step = 1024 / 44100
        prev_secs = None
        prev_key: float = -1
        for point in pitch.points.root:
            if point.x - self.first_bar_length < note.start_pos:
                continue
            elif point.x - self.first_bar_length > note.end_pos:
                break
            if point.y == -100:
                prev_secs = None
                prev_key = 0
            else:
                secs = self.synchronizer.get_actual_secs_from_ticks(point.x - self.first_bar_length)
                key = point.y / 100
                if prev_secs is not None:
                    key_interval_dict[portion.openclosed(prev_secs, secs)] = functools.partial(
                        linear_interpolation,  # type: ignore[call-arg]
                        start=(prev_secs, prev_key - note.key_number),
                        end=(secs, key - note.key_number),
                    )
                else:
                    key_interval_dict[portion.singleton(secs)] = key - note.key_number
                prev_secs = secs
                prev_key = key
        pitch_bends = [
            key_interval_dict.get(secs, 0)
            for secs in more_itertools.numeric_range(note_start_time, note_end_time, secs_step)
        ]
        return pitch_bends if any(pitch_bends) else []
