import dataclasses
from typing import Optional

from libresvip.model.base import (
    InstrumentalTrack,
    Note,
    ParamCurve,
    Point,
    Points,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
)

from .model import (
    MutaNote,
    MutaPoint,
    MutaProject,
    MutaTempo,
    MutaTimeSignature,
    MutaTrack,
    MutaTrackType,
)
from .options import InputOptions


@dataclasses.dataclass
class MutaParser:
    options: InputOptions

    def parse_project(self, muta_project: MutaProject) -> Project:
        time_signatures = self.parse_time_signatures(muta_project.time_signatures)
        tempos = self.parse_tempos(muta_project.tempos)
        singing_tracks = self.parse_singing_tracks(
            [
                track
                for track in muta_project.tracks
                if track.track_type == MutaTrackType.SONG
            ]
        )
        instrumental_tracks = self.parse_instrumental_tracks(
            [
                track
                for track in muta_project.tracks
                if track.track_type == MutaTrackType.AUDIO
            ]
        )
        return Project(
            time_signature_list=time_signatures,
            song_tempo_list=tempos,
            track_list=singing_tracks + instrumental_tracks,
        )

    def parse_time_signatures(
        self, muta_time_signatures: list[MutaTimeSignature]
    ) -> list[TimeSignature]:
        return [
            TimeSignature(
                bar_index=muta_time_signature.measure_position,
                numerator=muta_time_signature.numerator,
                denominator=muta_time_signature.denominator,
            )
            for muta_time_signature in muta_time_signatures
        ]

    def parse_tempos(self, muta_tempos: list[MutaTempo]) -> list[SongTempo]:
        return [
            SongTempo(
                position=muta_tempo.position,
                bpm=muta_tempo.bpm / 100,
            )
            for muta_tempo in muta_tempos
        ]

    def parse_singing_tracks(
        self, muta_singing_tracks: list[MutaTrack]
    ) -> list[SingingTrack]:
        track_list = []
        for muta_track in muta_singing_tracks:
            if muta_track.song_track_data is not None:
                singing_track = SingingTrack(
                    title=muta_track.name,
                    ai_singer_name="".join(
                        chr(char) for char in muta_track.song_track_data.singer_name
                    ).rstrip("\0"),
                    mute=muta_track.mute,
                    solo=muta_track.solo,
                    note_list=self.parse_notes(muta_track.song_track_data.notes),
                )
                if pitch := self.parse_pitch(
                    muta_track.song_track_data.params.pitch_data,
                    muta_track.song_track_data.start,
                ):
                    singing_track.edited_params.pitch = pitch
                track_list.append(singing_track)
        return track_list

    def parse_pitch(
        self, muta_pitch: list[MutaPoint], tick_offset: int
    ) -> Optional[ParamCurve]:
        pitch_points = [Point.start_point()]
        for muta_point in muta_pitch:
            pitch_points.append(
                Point(
                    x=muta_point.time + tick_offset,
                    y=(muta_point.value + 1200)
                    if 0 < muta_point.value < 12900
                    else -100,
                )
            )
        pitch_points.append(Point.end_point())
        if len(pitch_points) > 2:
            return ParamCurve(
                points=Points(root=pitch_points),
            )

    def parse_instrumental_tracks(
        self, muta_tracks: list[MutaTrack]
    ) -> list[InstrumentalTrack]:
        track_list = []
        for muta_track in muta_tracks:
            if muta_track.audio_track_data is not None:
                instrumental_track = InstrumentalTrack(
                    title=muta_track.name,
                    mute=muta_track.mute,
                    solo=muta_track.solo,
                    offset=muta_track.audio_track_data.start,
                    audio_file_path=muta_track.audio_track_data.file_path.rstrip("\0"),
                )
                track_list.append(instrumental_track)
        return track_list

    def parse_notes(self, muta_notes: list[MutaNote]) -> list[Note]:
        notes = []
        for muta_note in muta_notes:
            note = Note(
                start_pos=muta_note.start,
                length=muta_note.length,
                key_number=139 - muta_note.key,
                lyric="".join(chr(char) for char in muta_note.lyric).rstrip("\0"),
                pronunciation=muta_note.phoneme,
            )
            notes.append(note)
        return notes
