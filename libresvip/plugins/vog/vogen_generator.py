import dataclasses
from typing import List

from libresvip.model.base import (
    Note,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
    Track,
)

from .model import (
    VogenNote,
    VogenProject,
    VogenTrack,
)
from .options import OutputOptions


@dataclasses.dataclass
class VogenGenerator:
    options: OutputOptions

    def generate_project(self, project: Project) -> VogenProject:
        return VogenProject(
            bpm0=self.generate_tempos(project.song_tempo_list),
            timeSig0=self.generate_time_signatures(project.time_signature_list),
            utts=self.generate_tracks(project.track_list),
        )

    def generate_tempos(self, song_tempo_list: List[SongTempo]) -> float:
        return song_tempo_list[0].bpm

    def generate_time_signatures(self, time_signature_list: List[TimeSignature]) -> str:
        time_signature = time_signature_list[0]
        return f"{time_signature.numerator}/{time_signature.denominator}"

    def generate_tracks(self, track_list: List[Track]) -> List[VogenTrack]:
        tracks = []
        for i, track in enumerate(track_list):
            if isinstance(track, SingingTrack):
                tracks.append(
                    VogenTrack(
                        name=track.title,
                        singerId=track.ai_singer_name,
                        notes=self.generate_notes(track.note_list),
                    )
                )
        return tracks

    def generate_notes(self, note_list: List[Note]) -> List[VogenNote]:
        return [
            VogenNote(
                on=note.start_pos,
                dur=note.length,
                lyric=note.lyric,
                rom=note.pronunciation,
                pitch=note.key_number,
            )
            for note in note_list
        ]
