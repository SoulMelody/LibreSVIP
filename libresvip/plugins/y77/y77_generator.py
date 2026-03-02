import dataclasses
import math

import pypinyin

from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import (
    Note,
    Project,
    SingingTrack,
    TimeSignature,
)
from libresvip.model.pitch_simulator import PitchSimulator
from libresvip.model.portamento import PortamentoPitch

from .model import Y77Note, Y77Project
from .options import OutputOptions


@dataclasses.dataclass
class Y77Generator:
    options: OutputOptions
    synchronizer: TimeSynchronizer = dataclasses.field(init=False)
    first_bar_length: int = 0

    def generate_project(self, project: Project) -> Y77Project:
        if self.options.track_index < 0:
            first_singing_track = next(
                (
                    track
                    for track in project.track_list
                    if isinstance(track, SingingTrack) and track.note_list
                ),
                None,
            )
        else:
            first_singing_track = project.track_list[self.options.track_index]
            assert isinstance(first_singing_track, SingingTrack)
        self.first_bar_length = int(project.time_signature_list[0].bar_length())
        self.synchronizer = TimeSynchronizer(project.song_tempo_list, self.first_bar_length)
        y77_project = Y77Project(
            bars=100,
            bpm=project.song_tempo_list[0].bpm,
            bbar=project.time_signature_list[0].numerator,
            bbeat=project.time_signature_list[0].denominator,
        )
        if first_singing_track is not None:
            y77_project.notes = self.generate_notes(
                first_singing_track, [project.time_signature_list[0]]
            )
            y77_project.nnote = len(y77_project.notes)
        return y77_project

    def generate_notes(
        self, singing_track: SingingTrack, time_signatures: list[TimeSignature]
    ) -> list[Y77Note]:
        pitch_simulator = None
        y77_notes = []
        for note in singing_track.note_list:
            y77_note = Y77Note(
                lyric=note.lyric,
                start=round(note.start_pos / 30),
                length=round(note.length / 30),
                pitch=88 - note.key_number,
                py=note.pronunciation or " ".join(pypinyin.lazy_pinyin(note.lyric)),
            )
            if pitch_simulator is None:
                pitch_simulator = PitchSimulator(
                    synchronizer=self.synchronizer,
                    note_list=singing_track.note_list,
                    time_signature_list=time_signatures,
                    portamento=PortamentoPitch.no_portamento(),
                )
                pitch_simulator.merge_pitch_curve(
                    singing_track.edited_params.pitch, self.first_bar_length
                )
            y77_note.pit, y77_note.pbs = self.generate_pitch(pitch_simulator, note)
            y77_notes.append(y77_note)
        return y77_notes

    def generate_pitch(
        self, pitch_simulator: PitchSimulator, note: Note
    ) -> tuple[list[float], int]:
        tick_step = note.length / 500.0
        rel_pitch_values = [
            pitch_simulator.pitch_at_ticks(note.start_pos + int(tick_step * i)) / 100
            - (note.key_number)
            for i in range(500)
        ]

        max_abs_value = max(abs(value) for value in rel_pitch_values)
        pbs_for_this_note = min(math.ceil(max_abs_value), 12)
        y77_pitch_param = [
            rel_pitch_value * 50 / pbs_for_this_note + 50 for rel_pitch_value in rel_pitch_values
        ]

        return y77_pitch_param, pbs_for_this_note - 1
