import dataclasses

from libresvip.model.base import (
    Note,
    ParamCurve,
    Params,
    Point,
    Points,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
)

from .model import UFData, UFNotes, UFPitch, UFTempos, UFTimeSignatures, UFTracks
from .options import InputOptions


@dataclasses.dataclass
class UFDataParser:
    options: InputOptions

    def parse_project(self, ufdata_project: UFData) -> Project:
        uf_project = ufdata_project.project
        project = Project(
            song_tempo_list=self.parse_tempos(uf_project.tempos),
            time_signature_list=self.parse_time_signatures(uf_project.time_signatures),
            track_list=self.parse_tracks(uf_project.tracks),
        )
        return project

    @staticmethod
    def parse_tempos(tempos: list[UFTempos]) -> list[SongTempo]:
        return [
            SongTempo(
                position=tempo.tick_position,
                bpm=tempo.bpm,
            )
            for tempo in tempos
        ]

    @staticmethod
    def parse_time_signatures(
        time_signatures: list[UFTimeSignatures],
    ) -> list[TimeSignature]:
        return [
            TimeSignature(
                bar_index=time_signature.measure_position,
                numerator=time_signature.numerator,
                denominator=time_signature.denominator,
            )
            for time_signature in time_signatures
        ]

    def parse_tracks(self, tracks: list[UFTracks]) -> list[SingingTrack]:
        return [
            SingingTrack(
                title=track.name,
                note_list=self.parse_notes(track.notes),
                edited_params=self.parse_pitch(track.pitch),
            )
            for track in tracks
        ]

    @staticmethod
    def parse_pitch(pitch: UFPitch) -> Params:
        pitch_curve = ParamCurve(
            point_list=Points(
                root=[
                    Point(
                        x=tick,
                        y=round(value),
                    )
                    for tick, value in zip(pitch.ticks, pitch.values)
                ]
            )
        )
        return Params(
            pitch=pitch_curve,
        )

    @staticmethod
    def parse_notes(notes: list[UFNotes]) -> list[Note]:
        return [
            Note(
                start_pos=note.tick_on,
                length=note.tick_off - note.tick_on,
                key_number=note.key,
                lyric=note.lyric,
            )
            for note in notes
        ]
