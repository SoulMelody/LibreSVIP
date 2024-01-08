import dataclasses

from libresvip.core.tick_counter import shift_beat_list, shift_tempo_list
from libresvip.model.base import (
    Note,
    ParamCurve,
    Point,
    Points,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
)
from libresvip.model.relative_pitch_curve import RelativePitchCurve

from .model import UFData, UFNotes, UFPitch, UFTempos, UFTimeSignatures, UFTracks
from .options import InputOptions


@dataclasses.dataclass
class UFDataParser:
    options: InputOptions

    def parse_project(self, ufdata_project: UFData) -> Project:
        uf_project = ufdata_project.project
        time_signature_list = self.parse_time_signatures(uf_project.time_signatures)
        tick_prefix = int(time_signature_list[0].bar_length() * uf_project.measure_prefix)
        project = Project(
            song_tempo_list=shift_tempo_list(self.parse_tempos(uf_project.tempos), tick_prefix),
            time_signature_list=shift_beat_list(
                time_signature_list,
                uf_project.measure_prefix,
            ),
            track_list=self.parse_tracks(uf_project.tracks, tick_prefix),
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

    def parse_tracks(self, tracks: list[UFTracks], tick_prefix: int) -> list[SingingTrack]:
        track_list = []
        for track in tracks:
            singing_track = SingingTrack(
                title=track.name, note_list=self.parse_notes(track.notes, tick_prefix)
            )
            if track.pitch is not None:
                singing_track.edited_params.pitch = self.parse_pitch(
                    track.pitch, singing_track.note_list, tick_prefix
                )
            track_list.append(singing_track)
        return track_list

    @staticmethod
    def parse_pitch(pitch: UFPitch, note_list: list[Note], tick_prefix: int) -> ParamCurve:
        if pitch.is_absolute:
            return ParamCurve(
                points=Points(
                    root=[
                        Point(
                            x=tick + tick_prefix,
                            y=round(value),
                        )
                        for tick, value in zip(pitch.ticks, pitch.values)
                    ]
                )
            )
        rel_pitch_points = [
            Point(
                x=tick + tick_prefix,
                y=round(value),
            )
            for tick, value in zip(pitch.ticks, pitch.values)
        ]
        return RelativePitchCurve().to_absolute(rel_pitch_points, note_list)

    @staticmethod
    def parse_notes(notes: list[UFNotes], tick_prefix: int) -> list[Note]:
        return [
            Note(
                start_pos=note.tick_on,
                length=note.tick_off - note.tick_on + tick_prefix,
                key_number=note.key,
                lyric=note.lyric,
            )
            for note in notes
        ]
