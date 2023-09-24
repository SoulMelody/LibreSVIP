import dataclasses

from libresvip.core.constants import DEFAULT_BPM
from libresvip.core.lyric_phoneme.chinese import CHINESE_RE
from libresvip.model.base import (
    InstrumentalTrack,
    Note,
    Point,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
    Track,
)
from libresvip.utils import db_to_float

from .model import (
    UNote,
    USTXProject,
    UTempo,
    UTimeSignature,
    UTrack,
    UVoicePart,
    UWavePart,
)
from .options import InputOptions
from .util import BasePitchGenerator


@dataclasses.dataclass
class UstxParser:
    options: InputOptions
    base_pitch_generator: BasePitchGenerator = dataclasses.field(init=False)

    def parse_project(self, ustx_project: USTXProject) -> Project:
        self.base_pitch_generator = BasePitchGenerator(ustx_project)
        tempos = self.parse_tempos(ustx_project.tempos)
        time_signatures = self.parse_time_signatures(ustx_project.time_signatures)
        tracks = self.parse_tracks(ustx_project.tracks, ustx_project.voice_parts)
        for track in tracks:
            track.edited_params.pitch.points.append(Point.end_point())
        tracks.extend(
            self.parse_wave_parts(ustx_project.tracks, ustx_project.wave_parts)
        )
        return Project(
            song_tempo_list=tempos,
            time_signature_list=time_signatures,
            track_list=tracks,
        )

    @staticmethod
    def parse_tempos(tempos: list[UTempo]) -> list[SongTempo]:
        song_tempo_list = [
            SongTempo(
                position=tempo.position + 1920
                if tempo.position > 0
                else tempo.position,
                bpm=tempo.bpm,
            )
            for tempo in tempos
        ]
        if not len(song_tempo_list):
            song_tempo_list.append(SongTempo(position=0, bpm=DEFAULT_BPM))
        return song_tempo_list

    @staticmethod
    def parse_time_signatures(
        time_signatures: list[UTimeSignature],
    ) -> list[TimeSignature]:
        time_signature_list = [
            TimeSignature(
                bar_index=time_signature.bar_position,
                numerator=time_signature.beat_per_bar,
                denominator=time_signature.beat_unit,
            )
            for time_signature in time_signatures
        ]
        if not len(time_signature_list):
            time_signature_list.append(TimeSignature())
        return time_signature_list

    def parse_tracks(
        self, tracks: list[UTrack], voice_parts: list[UVoicePart]
    ) -> list[Track]:
        track_list = [
            SingingTrack(
                volume=self.parse_volume(ustx_track.volume),
                solo=ustx_track.solo,
                mute=ustx_track.mute,
                ai_singer_name=ustx_track.singer or "",
            )
            for ustx_track in tracks
            if ustx_track.singer
        ]
        for track in track_list:
            track.edited_params.pitch.points.append(Point.start_point())
        for voice_part in voice_parts:
            track_index = voice_part.track_no
            if track_index < len(track_list):
                track = track_list[track_index]
            else:
                continue
            if not track.title:
                track.title = voice_part.name
            notes = self.parse_notes(voice_part.notes, voice_part.position)
            track.note_list.extend(notes)
            track.edited_params.pitch.points.extend(self.parse_pitch(voice_part))
        return [track for track in track_list if len(track.note_list)]

    def parse_pitch(self, part: UVoicePart) -> list[tuple[int, int]]:
        pitch_start = self.base_pitch_generator.pitch_start
        pitch_interval = self.base_pitch_generator.pitch_interval
        first_bar_length = 1920

        pitches = self.base_pitch_generator.base_pitch(part)

        curve = next((c for c in part.curves if c.abbr == "pitd"), None)
        if curve is not None and not curve.is_empty:
            for i in range(len(pitches)):
                pitches[i] += curve.sample(pitch_start + i * pitch_interval)

        point_list = [Point(first_bar_length + part.position, -100)]
        point_list.extend(
            Point(
                first_bar_length + part.position + i * pitch_interval,
                int(pitches[i]),
            )
            for i in range(len(pitches))
        )
        point_list.append(
            Point(
                first_bar_length + part.position + len(pitches) * pitch_interval, -100
            )
        )
        return point_list

    def parse_notes(self, notes: list[UNote], tick_prefix: int) -> list[Note]:
        note_list = []
        for ustx_note in notes:
            note = Note(
                key_number=ustx_note.tone,
                lyric="-" if ustx_note.lyric.startswith("+") else ustx_note.lyric,
                start_pos=ustx_note.position + tick_prefix,
                length=ustx_note.duration,
            )
            if (CHINESE_RE.search(ustx_note.lyric) is None) and len(
                ustx_note.lyric
            ) > 1:
                note.pronunciation = ustx_note.lyric
            note_list.append(note)
        return note_list

    def parse_wave_parts(
        self, tracks: list[UTrack], wave_parts: list[UWavePart]
    ) -> list[InstrumentalTrack]:
        track_list = []
        for wave_part in wave_parts:
            ustx_track = tracks[wave_part.track_no]
            rel_path = wave_part.relative_path
            # duration = wave_part.file_duration_ms - wave_part.skip_ms - wave_part.trim_ms
            track_list.append(
                InstrumentalTrack(
                    audio_file_path=rel_path,
                    offset=wave_part.position,
                    title=wave_part.name,
                    mute=ustx_track.mute,
                    solo=ustx_track.solo,
                    volume=self.parse_volume(ustx_track.volume),
                )
            )
        return track_list

    def parse_volume(self, volume: int) -> float:
        return min(db_to_float(volume, using_amplitude=False), 2)
