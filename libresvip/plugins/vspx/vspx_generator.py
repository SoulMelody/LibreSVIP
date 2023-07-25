import bisect
import contextlib
import dataclasses
import math
from typing import Optional, Union

import more_itertools
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError
from xsdata.formats.dataclass.models.generics import AnyElement

from libresvip.model.base import (
    InstrumentalTrack,
    Note,
    ParamCurve,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
)
from libresvip.model.point import linear_interpolation
from libresvip.utils import midi2note

from .model import (
    PIT,
    VocalSharpBeat,
    VocalSharpDefaultTrill,
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


@dataclasses.dataclass
class VocalSharpGenerator:
    options: OutputOptions
    first_bar_length: int = dataclasses.field(init=False)

    def generate_project(self, project: Project) -> VocalSharpProject:
        vspx_project = VocalSharpProject()
        self.first_bar_length = round(project.time_signature_list[0].bar_length())
        vspx_project.project.elements.extend(
            [
                AnyElement(qname="SamplesPerSec", text=44100),
                AnyElement(qname="Resolution", text=1920),
            ]
        )
        vspx_project.project.elements.append(VocalSharpDefaultTrill())
        vspx_project.project.elements.extend(
            self.generate_tempos(project.song_tempo_list)
        )
        vspx_project.project.elements.extend(
            self.generate_time_signatures(project.time_signature_list)
        )
        singing_tracks = self.generate_singing_tracks(
            [track for track in project.track_list if isinstance(track, SingingTrack)]
        )
        vspx_project.project.elements.extend(singing_tracks)
        vspx_project.project.elements.extend(
            self.generate_instrumental_tracks(
                [
                    track
                    for track in project.track_list
                    if isinstance(track, InstrumentalTrack)
                ]
            )
        )
        max_duration = max(
            (
                note.pos + note.duration
                for track in singing_tracks
                for note in track.note
            ),
            default=0,
        )
        vspx_duration = (
            math.ceil(max(max_duration - 122880, 0) / 30720) * 30720 + 122880
        )
        vspx_project.project.elements.insert(
            2, AnyElement(qname="Duration", text=vspx_duration)
        )
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
        track_list = []
        for track in instrumental_tracks:
            with contextlib.suppress(CouldntDecodeError, FileNotFoundError):
                audio_segment = AudioSegment.from_file(track.audio_file_path)
                sequence = VocalSharpSequence(
                    name=track.title,
                    path=track.audio_file_path,
                    pos=track.offset,
                )
                if audio_segment.channels == 1:
                    track_list.append(
                        VocalSharpMonoTrack(
                            name=track.title,
                            is_mute=str(track.mute),
                            is_solo=str(track.solo),
                            sequences=[sequence],
                        )
                    )
                elif audio_segment.channels == 2:
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
            if pitch_points := self.generate_pitch(
                track.edited_params.pitch, track.note_list
            ):
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

    def generate_pitch(self, pitch: ParamCurve, note_list: list[Note]) -> list[PIT]:
        note_boundaries = [
            (prev_note.end_pos + next_note.start_pos) // 2
            for prev_note, next_note in more_itertools.pairwise(note_list)
        ]
        pitch_points = []
        prev_point: Optional[PIT] = None
        for point in pitch.points:
            cur_tick = point.x - self.first_bar_length
            note = note_list[
                min(
                    bisect.bisect_left(note_boundaries, cur_tick),
                    len(note_list) - 1,
                )
            ]
            if point.y > 0:
                if prev_point is not None:
                    cur_value = point.y - note.key_number * 100
                    for i in range(prev_point.time + 1, cur_tick):
                        pitch_points.append(
                            PIT(
                                time=prev_point.time + i,
                                value=round(
                                    linear_interpolation(
                                        (prev_point.time, prev_point.value),
                                        (cur_tick, cur_value),
                                        i,
                                    )
                                ),
                            )
                        )
                else:
                    pitch_points.append(
                        PIT(
                            time=cur_tick,
                            value=point.y - note.key_number * 100,
                        )
                    )
                prev_point = pitch_points[-1]
            else:
                prev_point = None
        return pitch_points
