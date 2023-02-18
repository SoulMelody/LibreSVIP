import dataclasses
from typing import List

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
            SongTempoList=self.parse_tempos(uf_project.tempos),
            TimeSignatureList=self.parse_time_signatures(uf_project.time_signatures),
            TrackList=self.parse_tracks(uf_project.tracks),
        )
        return project

    @staticmethod
    def parse_tempos(tempos: List[UFTempos]) -> List[SongTempo]:
        return [
            SongTempo(
                Position=tempo.tick_position,
                BPM=tempo.bpm,
            )
            for tempo in tempos
        ]

    @staticmethod
    def parse_time_signatures(
        time_signatures: List[UFTimeSignatures],
    ) -> List[TimeSignature]:
        return [
            TimeSignature(
                BarIndex=time_signature.measure_position,
                Numerator=time_signature.numerator,
                Denominator=time_signature.denominator,
            )
            for time_signature in time_signatures
        ]

    def parse_tracks(self, tracks: List[UFTracks]) -> List[SingingTrack]:
        return [
            SingingTrack(
                Title=track.name,
                NoteList=self.parse_notes(track.notes),
                EditedParams=self.parse_pitch(track.pitch),
            )
            for track in tracks
        ]

    @staticmethod
    def parse_pitch(pitch: UFPitch) -> Params:
        pitch_curve = ParamCurve(
            PointList=Points(
                __root__=[
                    Point(
                        x=tick,
                        y=round(value),
                    )
                    for tick, value in zip(pitch.ticks, pitch.values)
                ]
            )
        )
        return Params(
            Pitch=pitch_curve,
        )

    @staticmethod
    def parse_notes(notes: List[UFNotes]) -> List[Note]:
        return [
            Note(
                StartPos=note.tick_on,
                Length=note.tick_off - note.tick_on,
                KeyNumber=note.key,
                Lyric=note.lyric,
            )
            for note in notes
        ]
