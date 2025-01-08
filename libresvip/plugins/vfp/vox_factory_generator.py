import dataclasses
import math
import pathlib
import secrets

from libresvip.core.constants import DEFAULT_BPM, TICKS_IN_BEAT
from libresvip.core.time_sync import TimeSynchronizer
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
    prefix: str = dataclasses.field(init=False)
    audio_paths: dict[str, pathlib.Path] = dataclasses.field(default_factory=dict)
    synchronizer: TimeSynchronizer = dataclasses.field(init=False)

    def generate_project(self, project: Project) -> VOXFactoryProject:
        self.prefix = secrets.token_hex(5)
        self.synchronizer = TimeSynchronizer(project.song_tempo_list)
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
                clip_bank = self.generate_notes(track.note_list)
                clip_order = sorted(clip_bank.keys())
                track_bank[f"{self.prefix}-tr{i}"] = VOXFactoryVocalTrack(
                    clip_bank=clip_bank,
                    clip_order=clip_order,
                )
        return track_bank

    def generate_notes(self, notes: list[Note]) -> dict[str, VOXFactoryVocalClip]:
        note_bank = {}
        note_order = []
        max_ticks = notes[-1].end_pos if notes else 0
        max_quarter = max_ticks / TICKS_IN_BEAT
        for i, note in enumerate(notes):
            note_bank[f"{self.prefix}-no{i}"] = self.generate_note(note)
            note_order.append(f"{self.prefix}-no{i}")
        clip_count = math.ceil(max_quarter / 32)
        clip_bank = {}
        for i in range(clip_count):
            clip_bank[f"{self.prefix}-cl{i}"] = VOXFactoryVocalClip(
                start_quarter=32 * i,
                offset_quarter=32 * i,
                length=32,
                note_bank=note_bank,
                note_order=note_order,
            )
        return clip_bank

    def generate_note(self, note: Note) -> VOXFactoryNote:
        note_start_time = self.synchronizer.get_actual_secs_from_ticks(note.start_pos)
        return VOXFactoryNote(
            time=note_start_time,
            ticks=note.start_pos,
            duration_ticks=note.length,
            midi=note.key_number,
            name=note.lyric,
            syllable=note.pronunciation,
        )
