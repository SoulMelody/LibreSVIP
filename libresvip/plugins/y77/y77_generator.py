import dataclasses
from typing import List

from libresvip.model.base import (
    Note,
    Project,
    SingingTrack,
)

from .model import Y77Note, Y77Project
from .options import OutputOptions


@dataclasses.dataclass
class Y77Generator:
    options: OutputOptions

    def generate_project(self, project: Project) -> Y77Project:
        if self.options.track_index < 0:
            first_singing_track = next(
                (
                    track
                    for track in project.track_list
                    if isinstance(track, SingingTrack)
                ),
                None,
            )
        else:
            first_singing_track = project.track_list[self.options.track_index]
        y77_project = Y77Project(
            bars=100,
            bpm=project.song_tempo_list[0].bpm,
            bbar=project.time_signature_list[0].numerator,
            bbeat=project.time_signature_list[0].denominator,
        )
        if first_singing_track is not None:
            y77_project.notes = self.generate_notes(first_singing_track.note_list)
            y77_project.nnote = len(y77_project.notes)
        return y77_project

    def generate_notes(self, note_list: List[Note]) -> List[Y77Note]:
        return [
            Y77Note(
                lyric=note.lyric,
                start=round(note.start_pos / 30),
                len=round(note.length / 30),
                pitch=88 - note.key_number,
                py=note.pronunciation,
            )
            for note in note_list
        ]
