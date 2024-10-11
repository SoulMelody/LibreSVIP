import dataclasses
from typing import Optional, Union

from libresvip.core.tick_counter import shift_tempo_list
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import (
    InstrumentalTrack,
    Note,
    ParamCurve,
    Points,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
)
from libresvip.model.point import Point

from .model import (
    PIT,
    VocalSharpBeat,
    VocalSharpDefaultTrill,
    VocalSharpMonoTrack,
    VocalSharpNote,
    VocalSharpNoteTrack,
    VocalSharpProject,
    VocalSharpStereoTrack,
    VocalSharpTempo,
)
from .options import InputOptions
from .vspx_interval_dict import BasePitchCurve


@dataclasses.dataclass
class VocalSharpParser:
    options: InputOptions
    default_trill: Optional[VocalSharpDefaultTrill] = None
    synchronizer: TimeSynchronizer = dataclasses.field(init=False)
    first_bar_length: int = dataclasses.field(init=False)

    def parse_project(self, vspx_project: VocalSharpProject) -> Project:
        self.default_trill = vspx_project.project.default_trill
        time_signatures = self.parse_time_signatures(vspx_project.project.beat)
        self.first_bar_length = round(time_signatures[0].bar_length())
        tempos = self.parse_tempos(vspx_project.project.tempo)
        self.synchronizer = TimeSynchronizer(tempos)
        singing_tracks = self.parse_singing_tracks(
            [
                track
                for track in vspx_project.project.tracks
                if isinstance(track, VocalSharpNoteTrack)
            ]
        )
        instrumental_tracks = self.parse_instrumental_tracks(
            [
                track
                for track in vspx_project.project.tracks
                if isinstance(track, (VocalSharpMonoTrack, VocalSharpStereoTrack))
            ]
        )
        return Project(
            time_signature_list=time_signatures,
            song_tempo_list=tempos,
            track_list=singing_tracks + instrumental_tracks,
        )

    def parse_time_signatures(self, beat_list: list[VocalSharpBeat]) -> list[TimeSignature]:
        return [
            TimeSignature(
                bar_index=beat.bar_index,
                numerator=beat.beat_per_bar,
                denominator=beat.bar_divide,
            )
            for beat in beat_list
        ]

    def parse_tempos(self, tempo_list: list[VocalSharpTempo]) -> list[SongTempo]:
        return shift_tempo_list(
            [
                SongTempo(
                    position=tempo.pos,
                    bpm=tempo.bpm,
                )
                for tempo in tempo_list
            ],
            self.first_bar_length,
        )

    def parse_singing_tracks(self, track_list: list[VocalSharpNoteTrack]) -> list[SingingTrack]:
        tracks = []
        for track in track_list:
            singing_track = SingingTrack(
                title=track.name,
                mute=track.is_mute == "True",
                solo=track.is_solo == "True",
                ai_singer_name=track.singer,
                note_list=self.parse_notes(track.note),
            )
            if self.options.import_pitch:
                singing_track.edited_params.pitch = self.parse_pitch(track)
            tracks.append(singing_track)
        return tracks

    def parse_notes(self, note_list: list[VocalSharpNote]) -> list[Note]:
        return [
            Note(
                start_pos=note.pos,
                length=note.duration,
                key_number=note.key_number,
                lyric=note.lyric,
                pronunciation=note.lyric,
            )
            for note in note_list
        ]

    def parse_pitch(self, note_track: VocalSharpNoteTrack) -> ParamCurve:
        base_pitch_curve = BasePitchCurve(note_track, self.default_trill, self.synchronizer)
        pitch_points = [Point.start_point()]
        prev_tick = None
        for vspx_point in note_track.parameter.points:
            if isinstance(vspx_point, PIT):
                cur_tick = vspx_point.time + self.first_bar_length
                if prev_tick is None:
                    pitch_points.append(Point(x=cur_tick, y=-100))
                elif vspx_point.time - prev_tick > 1:
                    pitch_points.append(Point(x=prev_tick, y=-100))
                    pitch_points.append(Point(x=cur_tick, y=-100))
                vspx_point_secs = self.synchronizer.get_actual_secs_from_ticks(vspx_point.time)
                if (base_key := base_pitch_curve.semitone_value_at(vspx_point_secs)) is not None:
                    pitch_points.append(
                        Point(
                            x=cur_tick,
                            y=round(base_key * 100 + vspx_point.value),
                        )
                    )
                prev_tick = cur_tick
        if len(pitch_points) > 1:
            pitch_points.append(Point(x=pitch_points[-1].x, y=-100))
        pitch_points.append(Point.end_point())
        if len(pitch_points) <= 2:
            pitch_points.clear()
        return ParamCurve(points=Points(root=pitch_points))

    def parse_instrumental_tracks(
        self,
        track_list: list[Union[VocalSharpMonoTrack, VocalSharpStereoTrack]],
    ) -> list[InstrumentalTrack]:
        tracks = []
        if self.options.import_instrumental_track:
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
