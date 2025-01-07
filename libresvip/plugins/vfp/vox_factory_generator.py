import dataclasses
import pathlib

from libresvip.core.constants import DEFAULT_BPM
from libresvip.model.base import Note, Project, SingingTrack, SongTempo, TimeSignature, Track

from .model import (
    VOXFactoryNote,
    VOXFactoryProject,
    VOXFactoryTrack,
    VOXFactoryVocalClip,
    VOXFactoryVocalTrack,
)
from .options import OutputOptions


@dataclasses.dataclass
class VOXFactoryGenerator:
    options: OutputOptions
    audio_paths: dict[str, pathlib.Path] = dataclasses.field(default_factory=dict)

    def generate_project(self, project: Project) -> VOXFactoryProject:
        vox_project = VOXFactoryProject(
            tempo=self.generate_tempo(project.song_tempo_list),
            time_signature=self.generate_time_signature(project.time_signature_list),
            track_bank=self.generate_tracks(project.track_list),
        )
        vox_project.track_order = sorted(vox_project.track_bank.keys())
        return vox_project

    def generate_tempo(self, tempos: list[SongTempo]) -> float:
        return tempos[0].bpm if tempos else DEFAULT_BPM

    def generate_time_signature(self, time_signatures: list[TimeSignature]) -> list[int]:
        if time_signatures:
            return [time_signatures[0].numerator, time_signatures[0].denominator]
        else:
            return [4, 4]

    def generate_tracks(self, tracks: list[Track]) -> dict[str, VOXFactoryTrack]:
        track_bank = {}
        for i, track in enumerate(tracks):
            if isinstance(track, SingingTrack):
                note_list = self.generate_notes(track.note_list)
                clip_bank = {f"clip_{i}": clip for i, clip in enumerate(note_list)}
                clip_order = sorted(clip_bank.keys())
                track_bank[str(i)] = VOXFactoryVocalTrack(
                    clip_bank=clip_bank,
                    clip_order=clip_order,
                )
        return track_bank

    def generate_notes(self, notes: list[Note]) -> dict[str, VOXFactoryVocalClip]:
        note_bank = {}
        note_order = []
        for i, note in enumerate(notes):
            note_bank[f"note_{i}"] = self.generate_note(note)
            note_order.append(f"note_{i}")
        return {
            "clip": VOXFactoryVocalClip(
                note_bank=note_bank,
                note_order=note_order,
            ),
        }

    def generate_note(self, note: Note) -> VOXFactoryNote:
        return VOXFactoryNote(
            ticks=note.start_pos,
            duration_ticks=note.length,
            midi=note.key_number,
            name=note.lyric,
            syllable=note.pronunciation,
        )
