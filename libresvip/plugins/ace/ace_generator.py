from __future__ import annotations

import dataclasses
import hashlib
import pathlib
import time
from typing import TYPE_CHECKING

from libresvip.core.constants import DEFAULT_BPM, TICKS_IN_BEAT
from libresvip.core.lyric_phoneme.chinese import get_pinyin_series
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import InstrumentalTrack, Note, Project, SingingTrack, SongTempo
from libresvip.utils.audio import audio_track_info

from .model import (
    AceBgmInfo,
    AceBgmTrack,
    AceDebugInfo,
    AceNote,
    AcePitchBend,
    AceProject,
    AceRoleInfo,
    AceSongInfo,
    AceTrack,
)

if TYPE_CHECKING:
    from .options import OutputOptions

DEFAULT_SCALE = [84, 83, 81, 79, 77, 76, 74, 72, 71, 69, 67, 65, 64, 62, 60]


@dataclasses.dataclass
class AceMobileGenerator:
    options: OutputOptions
    synchronizer: TimeSynchronizer = dataclasses.field(init=False)
    first_bar_length: int = dataclasses.field(init=False)

    def generate_project(self, project: Project) -> AceProject:
        tempos = project.song_tempo_list or [SongTempo(bpm=DEFAULT_BPM)]
        self.synchronizer = TimeSynchronizer(tempos)
        self.first_bar_length = round(
            project.time_signature_list[0].bar_length()
            if project.time_signature_list
            else TICKS_IN_BEAT * 4
        )
        singing_tracks = [
            self.generate_track(track)
            for track in project.track_list
            if isinstance(track, SingingTrack)
        ]
        instrumental_tracks = [
            track for track in project.track_list if isinstance(track, InstrumentalTrack)
        ]
        duration = max(
            (
                self.synchronizer.get_actual_secs_from_ticks(note.end_pos)
                for track in project.track_list
                if isinstance(track, SingingTrack)
                for note in track.note_list
            ),
            default=0.0,
        )
        first_signature = project.time_signature_list[0] if project.time_signature_list else None
        return AceProject(
            version=2,
            debug_info=AceDebugInfo(),
            song_info=AceSongInfo(
                author=self.options.author,
                beat_of_bar=first_signature.numerator if first_signature else 4,
                bpm=tempos[0].bpm,
                duration=duration,
                first_beat_offset=self.first_note_time(project),
                key=self.options.key,
                name=self.options.song_name,
                operate_scale=DEFAULT_SCALE,
                scale=DEFAULT_SCALE,
                segment_of_beat=4,
                song_id=int(time.time() * 1000),
            ),
            bgm_info=self.generate_bgm_info(instrumental_tracks),
            tracks=singing_tracks,
        )

    def generate_track(self, track: SingingTrack) -> AceTrack:
        role_name = track.ai_singer_name or track.title or self.options.role_name
        notes = [self.generate_note(note, track) for note in track.note_list if note.length > 0]
        return AceTrack(
            front=True,
            lyric="".join(note.word for note in notes),
            mute=track.mute,
            notes=notes,
            pan=track.pan,
            role_info=AceRoleInfo(name=role_name, role_id=self.options.role_id),
            singer_volume=track.volume,
            solo=track.solo,
        )

    def generate_note(self, note: Note, track: SingingTrack) -> AceNote:
        lyric = note.lyric or "la"
        pinyin = note.pronunciation or self.generate_pronunciation(lyric)
        start_time = self.synchronizer.get_actual_secs_from_ticks(note.start_pos)
        end_time = self.synchronizer.get_actual_secs_from_ticks(note.end_pos)
        pitch_bends = []
        if self.options.export_pitch:
            for point in track.edited_params.pitch.points.root:
                tick = point.x - self.first_bar_length
                if note.start_pos <= tick <= note.end_pos and point.y != -100:
                    pitch_bends.append(
                        AcePitchBend(
                            time=self.synchronizer.get_actual_secs_from_ticks(tick),
                            pitch=point.y / 100 - note.key_number,
                        )
                    )
        return AceNote(
            br=note.head_tag == "V",
            config="",
            consonant_time_abs=(
                note.edited_phones.head_length_in_secs if note.edited_phones is not None else None
            ),
            end_time=end_time,
            key=self.options.key,
            pinyin=pinyin,
            pitch=note.key_number + 12,
            pitchBends=pitch_bends,
            scale=DEFAULT_SCALE,
            start_time=start_time,
            word=lyric,
        )

    @staticmethod
    def generate_pronunciation(lyric: str) -> str:
        pronunciation = get_pinyin_series([lyric])[0]
        return pronunciation or lyric

    def generate_bgm_info(self, tracks: list[InstrumentalTrack]) -> AceBgmInfo:
        bgm_tracks = []
        for track in tracks:
            path = pathlib.Path(track.audio_file_path)
            if not path.is_file():
                continue
            start_time = self.synchronizer.get_actual_secs_from_ticks(track.offset)
            track_info = audio_track_info(path)
            duration = track_info.duration if track_info is not None else 0.0
            bgm_tracks.append(
                AceBgmTrack(
                    end_time=start_time + duration,
                    file_md5=hashlib.md5(path.read_bytes()).hexdigest(),
                    file_name=path.stem,
                    file_type=path.suffix.lstrip(".").lower(),
                    position=start_time,
                    start_time=start_time,
                )
            )
        first_track = tracks[0] if tracks else None
        return AceBgmInfo(
            tracks=bgm_tracks,
            bgm_volume=first_track.volume if first_track is not None else 1.0,
            mute=first_track.mute if first_track is not None else False,
            solo=first_track.solo if first_track is not None else False,
        )

    def first_note_time(self, project: Project) -> float:
        first_pos = min(
            (
                note.start_pos
                for track in project.track_list
                if isinstance(track, SingingTrack)
                for note in track.note_list
            ),
            default=0,
        )
        return self.synchronizer.get_actual_secs_from_ticks(first_pos)
