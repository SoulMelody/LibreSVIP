import dataclasses

from pydub.utils import db_to_float

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

from .model import (
    UNote,
    USTXProject,
    UTempo,
    UTimeSignature,
    UTrack,
    UVibrato,
    UVoicePart,
    UWavePart,
)
from .options import InputOptions


@dataclasses.dataclass
class UstxParser:
    options: InputOptions

    def parse_project(self, ustx_project: USTXProject) -> Project:
        tempos = self.parse_tempos(ustx_project.tempos)
        time_signatures = self.parse_time_signatures(ustx_project.time_signatures)
        tracks = self.parse_tracks(ustx_project.tracks, ustx_project.voice_parts)
        for track in tracks:
            track.edited_params.pitch.points.append(Point.end_point())
        tracks.extend(
            self.parse_wave_parts(ustx_project.tracks, ustx_project.wave_parts)
        )
        return Project(
            SongTempoList=tempos,
            TimeSignatureList=time_signatures,
            TrackList=tracks,
        )

    @staticmethod
    def parse_tempos(tempos: list[UTempo]) -> list[SongTempo]:
        song_tempo_list = [
            SongTempo(
                Position=tempo.position + 1920
                if tempo.position > 0
                else tempo.position,
                BPM=tempo.bpm,
            )
            for tempo in tempos
        ]
        if not len(song_tempo_list):
            song_tempo_list.append(SongTempo(Position=0, BPM=DEFAULT_BPM))
        return song_tempo_list

    @staticmethod
    def parse_time_signatures(
        time_signatures: list[UTimeSignature],
    ) -> list[TimeSignature]:
        time_signature_list = [
            TimeSignature(
                BarIndex=time_signature.bar_position,
                Numerator=time_signature.beat_per_bar,
                Denominator=time_signature.beat_unit,
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
                Volume=self.parse_volume(ustx_track.volume),
                Solo=ustx_track.solo,
                Mute=ustx_track.mute,
                AISingerName=ustx_track.singer or "",
            )
            for ustx_track in tracks
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
            tick_prefix = voice_part.position
            notes = self.parse_notes(voice_part.notes, tick_prefix)
            track.note_list.extend(notes)
            track.edited_params.pitch.points.extend(
                self.parse_pitch(voice_part, tick_prefix)
            )
        return [track for track in track_list if len(track.note_list)]

    def parse_notes(self, notes: list[UNote], tick_prefix: int) -> list[Note]:
        note_list = []
        for ustx_note in notes:
            note = Note(
                KeyNumber=ustx_note.tone,
                Lyric="-" if ustx_note.lyric.startswith("+") else ustx_note.lyric,
                StartPos=ustx_note.position + tick_prefix,
                Length=ustx_note.duration,
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
                    AudioFilePath=rel_path,
                    Offset=wave_part.position,
                    Title=wave_part.name,
                    Mute=ustx_track.mute,
                    Solo=ustx_track.solo,
                    Volume=self.parse_volume(ustx_track.volume),
                )
            )
        return track_list

    def parse_volume(self, volume: int) -> float:
        return min(db_to_float(volume, using_amplitude=False), 2)
