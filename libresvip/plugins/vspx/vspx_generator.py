import dataclasses
import math
from typing import Optional, Union

from libresvip.core.tick_counter import skip_tempo_list
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import (
    InstrumentalTrack,
    Note,
    ParamCurve,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
)
from libresvip.utils.audio import audio_track_info
from libresvip.utils.music_math import linear_interpolation, midi2note

from .model import (
    PIT,
    VocalSharpBeat,
    VocalSharpMonoTrack,
    VocalSharpNote,
    VocalSharpNoteTrack,
    VocalSharpParameter,
    VocalSharpProject,
    VocalSharpSequence,
    VocalSharpStereoTrack,
    VocalSharpSyllable,
    VocalSharpTempo,
)
from .options import OutputOptions
from .vspx_interval_dict import BasePitchCurve


@dataclasses.dataclass
class VocalSharpGenerator:
    options: OutputOptions
    synchronizer: TimeSynchronizer = dataclasses.field(init=False)
    first_bar_length: int = dataclasses.field(init=False)

    def generate_project(self, project: Project) -> VocalSharpProject:
        vspx_project = VocalSharpProject()
        self.first_bar_length = round(project.time_signature_list[0].bar_length())
        self.synchronizer = TimeSynchronizer(project.song_tempo_list)
        vspx_project.project.tempo = self.generate_tempos(project.song_tempo_list)
        vspx_project.project.beat = self.generate_time_signatures(project.time_signature_list)
        singing_tracks = self.generate_singing_tracks(
            [track for track in project.track_list if isinstance(track, SingingTrack)]
        )
        vspx_project.project.tracks.extend(singing_tracks)
        vspx_project.project.tracks.extend(
            self.generate_instrumental_tracks(
                [track for track in project.track_list if isinstance(track, InstrumentalTrack)]
            )
        )
        max_duration = max(
            (note.pos + note.duration for track in singing_tracks for note in track.note),
            default=0,
        )
        vspx_duration = math.ceil(max(max_duration - 122880, 0) / 30720) * 30720 + 122880
        vspx_project.project.duration = vspx_duration
        return vspx_project

    def generate_time_signatures(
        self, time_signatures: list[TimeSignature]
    ) -> list[VocalSharpBeat]:
        return [
            VocalSharpBeat(
                bar_index=time_signature.bar_index,
                beat_per_bar=time_signature.numerator,
                bar_divide=time_signature.denominator,
            )
            for time_signature in time_signatures
        ]

    def generate_tempos(self, tempos: list[SongTempo]) -> list[VocalSharpTempo]:
        tempos = skip_tempo_list(tempos, self.first_bar_length)
        return [
            VocalSharpTempo(
                pos=tempo.position,
                bpm=tempo.bpm,
            )
            for tempo in tempos
        ]

    def generate_instrumental_tracks(
        self, instrumental_tracks: list[InstrumentalTrack]
    ) -> list[Union[VocalSharpMonoTrack, VocalSharpStereoTrack]]:
        track_list: list[Union[VocalSharpMonoTrack, VocalSharpStereoTrack]] = []
        for track in instrumental_tracks:
            if (track_info := audio_track_info(track.audio_file_path, only_wav=True)) is not None:
                sequence = VocalSharpSequence(
                    name=track.title,
                    path=track.audio_file_path,
                    pos=track.offset,
                )
                if track_info.channel_s == 1:
                    track_list.append(
                        VocalSharpMonoTrack(
                            name=track.title,
                            is_mute=str(track.mute),
                            is_solo=str(track.solo),
                            sequences=[sequence],
                        )
                    )
                elif track_info.channel_s == 2:
                    track_list.append(
                        VocalSharpStereoTrack(
                            name=track.title,
                            is_mute=str(track.mute),
                            is_solo=str(track.solo),
                            sequences=[sequence],
                        )
                    )
        return track_list

    def generate_singing_tracks(
        self, singing_tracks: list[SingingTrack]
    ) -> list[VocalSharpNoteTrack]:
        note_tracks = []
        for track in singing_tracks:
            note_track = VocalSharpNoteTrack(
                name=track.title,
                singer=track.ai_singer_name,
                is_mute=str(track.mute),
                is_solo=str(track.solo),
                note=self.generate_notes(track.note_list),
            )
            if pitch_points := self.generate_pitch(track.edited_params.pitch, note_track):
                note_track.parameter = VocalSharpParameter(points=pitch_points)
            note_tracks.append(note_track)
        return note_tracks

    def generate_notes(self, notes: list[Note]) -> list[VocalSharpNote]:
        return [
            VocalSharpNote(
                pos=note.start_pos,
                pitch=midi2note(note.key_number),
                duration=note.length,
                lyric=note.lyric or note.pronunciation,
                syllable=[VocalSharpSyllable()],
            )
            for note in notes
        ]

    def generate_pitch(self, pitch: ParamCurve, note_track: VocalSharpNoteTrack) -> list[PIT]:
        base_pitch_curve = BasePitchCurve(note_track, None, self.synchronizer)
        pitch_points: list[PIT] = []
        prev_point: Optional[PIT] = None
        for point in pitch.points.root:
            cur_tick = point.x - self.first_bar_length
            cur_secs = self.synchronizer.get_actual_secs_from_ticks(cur_tick)
            if (
                point.y > 0
                and (base_key := base_pitch_curve.semitone_value_at(cur_secs)) is not None
            ):
                if prev_point is not None:
                    cur_value = point.y - base_key * 100
                    pitch_points.extend(
                        PIT(
                            time=i,
                            value=round(
                                linear_interpolation(
                                    i,
                                    (prev_point.time, prev_point.value),
                                    (cur_tick, cur_value),
                                )
                            ),
                        )
                        for i in range(prev_point.time + 1, cur_tick)
                    )
                else:
                    pitch_points.append(
                        PIT(
                            time=cur_tick,
                            value=round(point.y - base_key * 100),
                        )
                    )
                prev_point = pitch_points[-1]
            else:
                prev_point = None
        return pitch_points
