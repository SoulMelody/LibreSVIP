import dataclasses
from typing import List

from libresvip.model.base import (
    Note,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
)

from .model import (
    VogenNote,
    VogenProject,
    VogenTrack,
)
from .options import InputOptions


@dataclasses.dataclass
class VogenParser:
    options: InputOptions

    def parse_project(self, vogen_project: VogenProject) -> Project:
        return Project(
            SongTempoList=self.parse_tempos(vogen_project.bpm0),
            TimeSignatureList=self.parse_time_signatures(vogen_project.time_sig0),
            TrackList=self.parse_tracks(vogen_project.utts),
        )

    def parse_tempos(self, bpm0: float) -> List[SongTempo]:
        return [SongTempo(Position=0, BPM=bpm0)]

    def parse_time_signatures(self, time_sig0: str) -> List[TimeSignature]:
        numerator, denominator = time_sig0.split("/")
        return [TimeSignature(Numerator=int(numerator), Denominator=int(denominator))]

    def parse_tracks(self, utts: List[VogenTrack]) -> List[SingingTrack]:
        return [
            SingingTrack(
                Title=utt.name,
                AISingerName=utt.singer_id,
                NoteList=self.parse_notes(utt.notes),
            )
            for utt in utts
        ]

    def parse_notes(self, notes: List[VogenNote]) -> List[Note]:
        return [
            Note(
                StartPos=note.on,
                Length=note.dur,
                Lyric=note.lyric,
                Pronunciation=note.rom,
                KeyNumber=note.pitch,
            )
            for note in notes
        ]
