import bisect
import dataclasses
from typing import Union

import more_itertools

from libresvip.model.base import (
    InstrumentalTrack,
    Note,
    ParamCurve,
    Point,
    Points,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
)
from libresvip.utils import hz2midi, midi2hz, note2midi

from .model import (
    PIT,
    VocalSharpBeat,
    VocalSharpMonoTrack,
    VocalSharpNote,
    VocalSharpNoteTrack,
    VocalSharpParameter,
    VocalSharpProject,
    VocalSharpStereoTrack,
    VocalSharpTempo,
)
from .options import InputOptions


@dataclasses.dataclass
class VocalSharpParser:
    options: InputOptions
    first_bar_length: int = dataclasses.field(init=False)

    def parse_project(self, vspx_project: VocalSharpProject) -> Project:
        time_signatures = self.parse_time_signatures(
            [
                track
                for track in vspx_project.project.elements
                if isinstance(track, VocalSharpBeat)
            ]
        )
        self.first_bar_length = time_signatures[0].bar_length()
        tempos = self.parse_tempos(
            [
                track
                for track in vspx_project.project.elements
                if isinstance(track, VocalSharpTempo)
            ]
        )
        singing_tracks = self.parse_singing_tracks(
            [
                track
                for track in vspx_project.project.elements
                if isinstance(track, VocalSharpNoteTrack)
            ]
        )
        instrumental_tracks = self.parse_instrumental_tracks(
            [
                track
                for track in vspx_project.project.elements
                if isinstance(track, (VocalSharpMonoTrack, VocalSharpStereoTrack))
            ]
        )
        return Project(
            time_signature_list=time_signatures,
            song_tempo_list=tempos,
            track_list=singing_tracks + instrumental_tracks,
        )

    def parse_time_signatures(
        self, beat_list: list[VocalSharpBeat]
    ) -> list[TimeSignature]:
        return [
            TimeSignature(
                bar_index=beat.bar_index,
                numerator=beat.beat_per_bar,
                denominator=beat.bar_divide,
            )
            for beat in beat_list
        ]

    def parse_tempos(self, tempo_list: list[VocalSharpTempo]) -> list[SongTempo]:
        return [
            SongTempo(
                position=tempo.pos,
                bpm=tempo.bpm,
            )
            for tempo in tempo_list
        ]

    def parse_singing_tracks(
        self, track_list: list[VocalSharpNoteTrack]
    ) -> list[SingingTrack]:
        tracks = []
        for track in track_list:
            singing_track = SingingTrack(
                title=track.name,
                mute=track.is_mute == "True",
                solo=track.is_solo == "True",
                ai_singer_name=track.singer,
                note_list=self.parse_notes(track.note),
            )
            singing_track.edited_params.pitch = self.parse_pitch(
                track.parameter, singing_track.note_list
            )
            tracks.append(singing_track)
        return tracks

    def parse_notes(self, note_list: list[VocalSharpNote]) -> list[Note]:
        return [
            Note(
                start_pos=note.pos,
                length=note.duration,
                key_number=note2midi(note.pitch),
                lyric=note.lyric,
                pronunciation=note.lyric,
            )
            for note in note_list
        ]

    def parse_pitch(
        self, parameter: VocalSharpParameter, note_list: list[Note]
    ) -> ParamCurve:
        note_boundaries = [
            (prev_note.end_pos + next_note.start_pos) // 2
            for prev_note, next_note in more_itertools.pairwise(note_list)
        ]
        pitch_points = [Point.start_point()]
        prev_tick = None
        for vspx_point in parameter.points:
            if isinstance(vspx_point, PIT):
                cur_tick = vspx_point.time + self.first_bar_length
                if prev_tick is None:
                    pitch_points.append(Point(x=cur_tick, y=-100))
                elif vspx_point.time - prev_tick > 1:
                    pitch_points.append(Point(x=prev_tick, y=-100))
                    pitch_points.append(Point(x=cur_tick, y=-100))
                note = note_list[
                    min(
                        bisect.bisect_left(note_boundaries, vspx_point.time),
                        len(note_list) - 1,
                    )
                ]
                param_freq = midi2hz(
                    note.key_number, a4_midi=57
                ) + vspx_point.value * 10 / (90 - note.key_number)
                if (
                    param_freq > 0
                    and (pit_value := hz2midi(param_freq, a4_midi=57)) > 0
                ):
                    pitch_points.append(
                        Point(
                            x=cur_tick,
                            y=round(pit_value * 100),
                        )
                    )
                prev_tick = cur_tick
        if len(pitch_points):
            pitch_points.append(Point(x=pitch_points[-1].x, y=-100))
        pitch_points.append(Point.end_point())
        if len(pitch_points):
            return ParamCurve(points=Points(root=pitch_points))

    def parse_instrumental_tracks(
        self, track_list: list[Union[VocalSharpMonoTrack, VocalSharpStereoTrack]]
    ) -> list[InstrumentalTrack]:
        tracks = []
        for track in track_list:
            for i, sequence in enumerate(track.sequences):
                instrumental_track = InstrumentalTrack(
                    title=sequence.name or f"{track.name} {i + 1}",
                    mute=track.is_mute == "True",
                    solo=track.is_solo == "True",
                    offset=sequence.pos,
                    audio_file_path=sequence.path,
                )
                tracks.append(instrumental_track)
        return tracks
