import dataclasses
import functools
import math
import operator

import more_itertools
import portion

from libresvip.core.tick_counter import shift_tempo_list
from libresvip.core.time_interval import PiecewiseIntervalDict
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import (
    InstrumentalTrack,
    Note,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
    Track,
)
from libresvip.model.point import Point
from libresvip.utils.music_math import db_to_float, ratio_to_db

from .model import (
    TuneLabAudioPart,
    TuneLabMidiPart,
    TuneLabNote,
    TuneLabPoints,
    TuneLabProject,
    TuneLabTempo,
    TuneLabTimeSignature,
    TuneLabTrack,
    TuneLabVibrato,
)
from .options import InputOptions


@dataclasses.dataclass
class TuneLabParser:
    options: InputOptions
    first_bar_length: int = dataclasses.field(init=False)
    synchronizer: TimeSynchronizer = dataclasses.field(init=False)

    def parse_project(self, project: TuneLabProject) -> Project:
        time_signature_list = self.parse_time_signatures(project.time_signatures)
        self.first_bar_length = round(time_signature_list[0].bar_length())
        tempo_list = self.parse_tempos(project.tempos)
        self.synchronizer = TimeSynchronizer(tempo_list)
        return Project(
            song_tempo_list=tempo_list,
            time_signature_list=time_signature_list,
            track_list=self.parse_tracks(project.tracks),
        )

    def parse_time_signatures(
        self, time_signatures: list[TuneLabTimeSignature]
    ) -> list[TimeSignature]:
        return [
            TimeSignature(
                bar_index=time_signature.bar_index,
                numerator=time_signature.numerator,
                denominator=time_signature.denominator,
            )
            for time_signature in time_signatures
        ]

    def parse_tempos(self, tempos: list[TuneLabTempo]) -> list[SongTempo]:
        return shift_tempo_list(
            [SongTempo(position=int(tempo.pos), bpm=tempo.bpm) for tempo in tempos],
            self.first_bar_length,
        )

    def parse_tracks(self, tracks: list[TuneLabTrack]) -> list[Track]:
        track_list = []
        for track in tracks:
            for part in track.parts:
                if isinstance(part, TuneLabAudioPart) and self.options.import_instrumental_track:
                    track_list.append(
                        InstrumentalTrack(
                            audio_file_path=part.path,
                            title=part.name,
                            offset=int(part.pos),
                            volume=self.parse_volume(track.gain),
                            pan=track.pan,
                            mute=track.mute,
                            solo=track.solo,
                        )
                    )
                elif isinstance(part, TuneLabMidiPart) and len(part.notes):
                    if (
                        len(track_list)
                        and isinstance(track_list[-1], SingingTrack)
                        and (
                            not track_list[-1].note_list
                            or track_list[-1].note_list[-1].end_pos <= int(part.pos)
                        )
                    ):
                        singing_track = track_list[-1]
                    else:
                        singing_track = SingingTrack(
                            title=part.name,
                            volume=self.parse_volume(track.gain),
                            pan=track.pan,
                            mute=track.mute,
                            solo=track.solo,
                        )
                        track_list.append(singing_track)
                    singing_track.note_list.extend(self.parse_notes(part.notes, int(part.pos)))
                    if self.options.import_pitch:
                        (
                            vibrato_base_interval_dict,
                            vibrato_envelope_interval_dict,
                        ) = self.parse_vibrato(part)
                        if pitch_points := self.parse_pitch(
                            part.pitch,
                            int(part.pos),
                            vibrato_base_interval_dict,
                            vibrato_envelope_interval_dict,
                        ):
                            singing_track.edited_params.pitch.points.root.extend(pitch_points)
        return track_list

    @staticmethod
    def parse_volume(gain: float) -> float:
        if gain >= 0:
            return min(gain / (ratio_to_db(4)) + 1.0, 2.0)
        else:
            return db_to_float(gain)

    @staticmethod
    def parse_notes(notes: list[TuneLabNote], offset: int) -> list[Note]:
        return [
            Note(
                start_pos=int(tlp_note.pos + offset),
                length=int(tlp_note.dur),
                key_number=tlp_note.pitch,
                lyric=tlp_note.lyric,
                pronunciation=tlp_note.pronunciation,
            )
            for tlp_note in notes
        ]

    @staticmethod
    def vibrato_value(seconds: float, vibrato_start: float, vibrato: TuneLabVibrato) -> float:
        return (
            math.sin(math.pi * (2 * (seconds - vibrato_start) * vibrato.frequency - vibrato.phase))
            * vibrato.amplitude
        )

    def parse_vibrato(
        self, part: TuneLabMidiPart
    ) -> tuple[PiecewiseIntervalDict, PiecewiseIntervalDict]:
        vibrato_base_interval_dict = PiecewiseIntervalDict()
        vibrato_envelope_interval_dict = PiecewiseIntervalDict()
        for vibrato in part.vibratos:
            vibrato_start = self.synchronizer.get_actual_secs_from_ticks(int(vibrato.pos))
            vibrato_end = self.synchronizer.get_actual_secs_from_ticks(
                int(vibrato.pos + vibrato.dur)
            )
            vibrato_base_interval_dict[portion.closed(vibrato_start, vibrato_end)] = (
                functools.partial(
                    self.vibrato_value,
                    vibrato_start=vibrato_start,
                    vibrato=vibrato,
                )
            )
        if part.automations is not None and part.automations["VibratoEnvelope"] is not None:
            for value, ticks_group in more_itertools.groupby_transform(
                part.automations["VibratoEnvelope"].values.root,
                keyfunc=operator.attrgetter("value"),
                valuefunc=operator.attrgetter("pos"),
            ):
                ticks_group = list(ticks_group)
                group_start = self.synchronizer.get_actual_secs_from_ticks(int(ticks_group[0]))
                group_end = self.synchronizer.get_actual_secs_from_ticks(int(ticks_group[-1] + 5))
                vibrato_envelope_interval_dict[
                    portion.closedopen(
                        group_start,
                        group_end,
                    )
                ] = max(value + 1, 0)
        return vibrato_base_interval_dict, vibrato_envelope_interval_dict

    def parse_pitch(
        self,
        pitch: list[TuneLabPoints],
        offset: int,
        vibrato_base_interval_dict: PiecewiseIntervalDict,
        vibrato_envelope_interval_dict: PiecewiseIntervalDict,
    ) -> list[Point]:
        points: list[Point] = [Point.start_point()]
        for pitch_part in pitch:
            for is_first, is_last, tlp_point in more_itertools.mark_ends(pitch_part.root):
                pitch_pos = int(tlp_point.pos) + offset
                if is_first:
                    points.append(
                        Point(
                            x=pitch_pos + self.first_bar_length,
                            y=-100,
                        )
                    )
                pitch_secs = self.synchronizer.get_actual_secs_from_ticks(pitch_pos)
                pitch_value = tlp_point.value
                if (vibrato_value := vibrato_base_interval_dict.get(pitch_secs)) is not None:
                    vibrato_value *= vibrato_envelope_interval_dict.get(pitch_secs, 1)
                    pitch_value += vibrato_value
                points.append(
                    Point(
                        x=pitch_pos + self.first_bar_length,
                        y=round(pitch_value * 100),
                    )
                )
                if is_last:
                    points.append(
                        Point(
                            x=points[-1].x,
                            y=-100,
                        )
                    )
        points.append(Point.end_point())
        return points
