from __future__ import annotations

import dataclasses
import math
import re
from typing import TYPE_CHECKING

from libresvip.core.constants import DEFAULT_BPM
from libresvip.core.lyric_phoneme.chinese import get_pinyin_series
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import (
    InstrumentalTrack,
    Note,
    Phones,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
)
from libresvip.model.point import Point

from .options import BpmSource

if TYPE_CHECKING:
    import pathlib

    from .model import AceBgmTrack, AceBreathNote, AceNote, AceProject, AceTrack
    from .options import InputOptions


@dataclasses.dataclass
class AceMobileParser:
    options: InputOptions
    path: pathlib.Path
    synchronizer: TimeSynchronizer = dataclasses.field(init=False)
    first_bar_length: int = dataclasses.field(init=False)
    project_version: int = dataclasses.field(init=False)

    def parse_project(self, ace_project: AceProject) -> Project:
        self.project_version = ace_project.version
        bpm = self.select_bpm(ace_project)
        tempos = [SongTempo(position=0, bpm=bpm)]
        time_signatures = [
            TimeSignature(
                bar_index=0,
                numerator=max(1, ace_project.song_info.beat_of_bar),
                denominator=4,
            )
        ]
        self.first_bar_length = round(time_signatures[0].bar_length())
        self.synchronizer = TimeSynchronizer(tempos)
        return Project(
            song_tempo_list=tempos,
            time_signature_list=time_signatures,
            track_list=[
                *self.parse_singing_tracks(ace_project.singing_tracks()),
                *self.parse_instrumental_tracks(ace_project),
            ],
        )

    def select_bpm(self, ace_project: AceProject) -> float:
        song_bpm = ace_project.song_info.bpm
        bgm_bpm = next(
            (
                track.bpm
                for track in ace_project.bgm_info.tracks
                if track.bpm is not None and track.bpm > 0
            ),
            None,
        )
        if self.options.bpm_source == BpmSource.SONG_INFO:
            return song_bpm if song_bpm > 0 else DEFAULT_BPM
        if self.options.bpm_source == BpmSource.BGM_INFO:
            return bgm_bpm or (song_bpm if song_bpm > 0 else DEFAULT_BPM)
        return bgm_bpm or (song_bpm if song_bpm > 0 else DEFAULT_BPM)

    def parse_singing_tracks(self, ace_tracks: list[AceTrack]) -> list[SingingTrack]:
        tracks = []
        for ace_track in ace_tracks:
            notes, pitch_points, strength_points = self.parse_notes(
                ace_track.notes, ace_track.br_notes
            )
            track = SingingTrack(
                title=ace_track.role_info.name,
                mute=ace_track.mute,
                solo=ace_track.solo,
                pan=ace_track.pan,
                volume=ace_track.singer_volume,
                ai_singer_name=ace_track.role_info.name,
                note_list=notes,
            )
            if self.options.import_pitch and pitch_points:
                pitch_points.sort(key=lambda point: point.x)
                pitch_points.insert(0, Point.start_point())
                pitch_points.append(Point.end_point())
                track.edited_params.pitch.points.root = pitch_points
            if self.options.import_strength and strength_points:
                strength_points.sort(key=lambda point: point.x)
                strength_points.insert(0, Point.start_point(0))
                strength_points.append(Point.end_point(0))
                track.edited_params.strength.points.root = strength_points
            tracks.append(track)
        return tracks

    def parse_notes(
        self, ace_notes: list[AceNote], breath_notes: list[AceBreathNote]
    ) -> tuple[list[Note], list[Point], list[Point]]:
        notes = []
        pitch_points = []
        strength_points: dict[int, Point] = {}
        breath_end_times = [breath.end_time for breath in breath_notes]
        for ace_note in sorted(ace_notes, key=lambda note: note.start_time):
            real_pitch = ace_note.pitch - 12 if self.project_version < 3 else ace_note.pitch
            start_pos = round(self.synchronizer.get_actual_ticks_from_secs(ace_note.start_time))
            end_pos = round(self.synchronizer.get_actual_ticks_from_secs(ace_note.end_time))
            if end_pos <= start_pos:
                end_pos = start_pos + 1
            lyric = self.select_lyric(ace_note)
            pinyin = ace_note.pinyin.strip()
            note = Note(
                lyric=lyric,
                pronunciation=pinyin if pinyin and lyric != pinyin else None,
                key_number=real_pitch,
                start_pos=start_pos,
                length=end_pos - start_pos,
                head_tag=(
                    "V"
                    if ace_note.br
                    or any(
                        math.isclose(
                            ace_note.start_time,
                            end_time,
                            rel_tol=0.0,
                            abs_tol=1e-6,
                        )
                        for end_time in breath_end_times
                    )
                    else None
                ),
                edited_phones=(
                    Phones(head_length_in_secs=ace_note.consonant_time_abs)
                    if ace_note.consonant_time_abs is not None
                    else None
                ),
            )
            source_pitch = ace_note.user_pitch or ace_note.pitch_bends
            if self.options.import_pitch and source_pitch:
                note_pitch_points = [
                    Point(
                        x=round(
                            self.synchronizer.get_actual_ticks_from_secs(pitch_bend.time)
                            + self.first_bar_length
                        ),
                        y=round((real_pitch + pitch_bend.pitch) * 100),
                    )
                    for pitch_bend in source_pitch
                    if pitch_bend.time <= ace_note.end_time
                ]
                if note_pitch_points:
                    note_pitch_points.sort(key=lambda point: point.x)
                    note_end_x = end_pos + self.first_bar_length
                    if note_pitch_points[-1].x < note_end_x:
                        note_pitch_points.append(Point(note_end_x, note_pitch_points[-1].y))
                    note_pitch_points.insert(0, Point(note_pitch_points[0].x, -100))
                    note_pitch_points.append(Point(note_end_x, -100))
                    pitch_points.extend(note_pitch_points)
            if self.options.import_strength and ace_note.energy_envolope:
                note_strength_points = [
                    Point(
                        x=round(
                            self.synchronizer.get_actual_ticks_from_secs(envelope_point.time)
                            + self.first_bar_length
                        ),
                        y=max(-1000, min(1000, round((envelope_point.envolope - 1) * 1000))),
                    )
                    for envelope_point in ace_note.energy_envolope
                ]
                note_strength_points.sort(key=lambda point: point.x)
                first_x = note_strength_points[0].x
                last_x = note_strength_points[-1].x
                strength_points.setdefault(first_x - 1, Point(first_x - 1, 0))
                for point in note_strength_points:
                    strength_points[point.x] = point
                strength_points.setdefault(last_x + 1, Point(last_x + 1, 0))
            notes.append(note)
        return notes, pitch_points, list(strength_points.values())

    @staticmethod
    def select_lyric(note: AceNote) -> str:
        word = note.word.strip()
        pinyin = note.pinyin.strip()
        if word and re.search(r"[\u3400-\u9fff]", word) and pinyin:
            default_pinyin = get_pinyin_series([word])[0]
            if pinyin.casefold() != default_pinyin.casefold():
                return pinyin
        if word and (
            word.isascii() or re.search(r"[\u3400-\u9fff\u3040-\u30ff\uac00-\ud7af]", word)
        ):
            return word
        return pinyin or word or "la"

    def parse_instrumental_tracks(self, ace_project: AceProject) -> list[InstrumentalTrack]:
        if not self.options.import_instrumental_track or hasattr(self.path, "protocol"):
            return []
        return [
            InstrumentalTrack(
                title=bgm_track.file_name,
                mute=ace_project.bgm_info.mute,
                solo=ace_project.bgm_info.solo,
                volume=ace_project.bgm_info.bgm_volume,
                audio_file_path=str(audio_path),
                offset=round(
                    self.synchronizer.get_actual_ticks_from_secs(
                        bgm_track.position or bgm_track.start_time
                    )
                ),
            )
            for bgm_track in ace_project.bgm_info.tracks
            if (audio_path := self.find_audio_path(bgm_track))
        ]

    def find_audio_path(self, bgm_track: AceBgmTrack) -> pathlib.Path | None:
        suffix = bgm_track.file_type.lstrip(".")
        candidates = [self.path.parent / f"{bgm_track.file_name}.{suffix}"]
        if bgm_track.file_md5:
            candidates.append(
                self.path.parent.parent
                / "local"
                / "assets_res"
                / "bgms"
                / f"{bgm_track.file_md5}.{suffix}"
            )
        return next((candidate for candidate in candidates if candidate.is_file()), None)
