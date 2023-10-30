import dataclasses

import pypinyin

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
            time_sig0=self.generate_time_signatures(project.time_signature_list),
            utts=self.generate_tracks(project.track_list),
        )

    def generate_tempos(self, song_tempo_list: list[SongTempo]) -> float:
        return song_tempo_list[0].bpm

    def generate_time_signatures(self, time_signature_list: list[TimeSignature]) -> str:
        time_signature = time_signature_list[0]
        return f"{time_signature.numerator}/{time_signature.denominator}"

    def generate_tracks(self, track_list: list[Track]) -> list[VogenTrack]:
        tracks = []
        for i, track in enumerate(track_list):
            if isinstance(track, SingingTrack):
                tracks.append(
                    VogenTrack(
                        name=track.title,
                        singer_id=track.ai_singer_name,
                        notes=self.generate_notes(track.note_list),
                    )
                )
        return tracks

    def generate_notes(self, note_list: list[Note]) -> list[VogenNote]:
        return [
            VogenNote(
                on=note.start_pos,
                dur=note.length,
                lyric=note.lyric,
                rom=note.pronunciation or " ".join(pypinyin.lazy_pinyin(note.lyric)),
                pitch=note.key_number,
            )
            for note in note_list
        ]
