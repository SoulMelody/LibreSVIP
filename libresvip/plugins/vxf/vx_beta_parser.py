import collections
import dataclasses
import math
import operator
from typing import Annotated

from construct import Container

from libresvip.core.constants import TICKS_IN_BEAT
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.core.warning_types import show_warning
from libresvip.model.base import Note, Project, SingingTrack, SongTempo, TimeSignature
from libresvip.model.point import Point
from libresvip.utils.translation import gettext_lazy as _

from .model import VxFile, VxPitchData, VxTrack
from .options import InputOptions


@dataclasses.dataclass
class VxBetaParser:
    options: InputOptions
    ticks_per_beat: int = dataclasses.field(init=False)
    first_bar_length: int = dataclasses.field(init=False)

    @property
    def tick_rate(self) -> float:
        if self.ticks_per_beat is not None:
            return TICKS_IN_BEAT / self.ticks_per_beat
        return 1

    def parse_project(self, vx_project: Annotated[Container, VxFile]) -> Project:
        self.ticks_per_beat = vx_project.ticks_per_beat
        self._convert_delta_to_cumulative(vx_project.tracks)
        time_signature_list = []
        if len(vx_project.tracks) > 0:
            master_track = vx_project.tracks[0]
            time_signature_list.extend(self.parse_time_signatures(master_track))
        song_tempo_list = self.parse_tempos(vx_project.tracks)
        self.synchronizer = TimeSynchronizer(song_tempo_list)
        return Project(
            song_tempo_list=song_tempo_list,
            time_signature_list=time_signature_list,
            track_list=self.parse_tracks(vx_project.tracks),
        )

    @staticmethod
    def _convert_delta_to_cumulative(tracks: list[Annotated[Container, VxTrack]]) -> None:
        for track in tracks:
            tick = 0
            for event in track.events:
                event.time += tick
                tick = event.time

    def parse_tempos(self, tracks: list[Annotated[Container, VxTrack]]) -> list[SongTempo]:
        tempos: list[SongTempo] = []

        # traversing
        for track in tracks:
            for event in track.events:
                if event.type == "set_tempo":
                    # convert tempo to BPM
                    tempo = round(event.tempo, 3)
                    tick = round(event.time * self.tick_rate)
                    last_tempo = tempos[-1].bpm if tempos else None
                    if tempo != last_tempo:
                        tempos.append(SongTempo(position=tick, bpm=tempo))
        if not tempos:
            # default bpm
            show_warning(_("No tempo labels found in the imported project."))
            tempos.append(SongTempo(position=0, bpm=self.options.default_bpm))
        else:
            tempos.sort(key=operator.attrgetter("position"))
        return tempos

    def parse_time_signatures(
        self, master_track: Annotated[Container, VxTrack]
    ) -> list[TimeSignature]:
        # no default
        time_signature_changes: list[TimeSignature] = []

        # traversing
        prev_ticks = 0
        measure = 0
        for event in master_track.events:
            if event.type == "time_signature":
                tick = event.time
                if not time_signature_changes:
                    tick_in_full_note = 4 * self.ticks_per_beat
                else:
                    tick_in_full_note = round(
                        time_signature_changes[-1].bar_length(self.ticks_per_beat)
                    )
                measure += (tick - prev_ticks) / tick_in_full_note
                ts_obj = TimeSignature(
                    bar_index=math.floor(measure),
                    numerator=event.numerator,
                    denominator=event.denominator,
                )
                time_signature_changes.append(ts_obj)
                prev_ticks = tick
        if not time_signature_changes or time_signature_changes[0].bar_index > 0:
            time_signature_changes.insert(0, TimeSignature(bar_index=0, numerator=4, denominator=4))
        self.first_bar_length = round(time_signature_changes[0].bar_length())
        return time_signature_changes

    def parse_track(self, track: Annotated[Container, VxTrack]) -> SingingTrack:
        lyrics: dict[int, str] = collections.defaultdict(lambda: "l-aa")
        prev_index = None
        for event in track.events:
            if event.type == "lyrics":
                seq_stat = (event.seq_stat - 16) // 64
                if seq_stat == 0:
                    lyrics[event.seq_num] = event.text
                    prev_index = None
                elif seq_stat == 1:
                    lyrics[event.seq_num] = event.text
                    prev_index = event.seq_num
                elif seq_stat == 2 and prev_index is not None:
                    lyrics[prev_index] += event.text
                elif seq_stat == 3 and prev_index is not None:
                    lyrics[prev_index] += event.text
                    prev_index = None
        last_note_on = None
        notes: list[Note] = []
        for event in track.events:
            if event.type == "note_on":
                last_note_on = event
            elif event.type == "note_off" and last_note_on:
                notes.append(
                    Note(
                        start_pos=round(last_note_on.time * self.tick_rate),
                        length=round((event.time - last_note_on.time) * self.tick_rate),
                        lyric=lyrics[len(notes)],
                        key_number=event.note,
                    )
                )
                last_note_on = None
        singing_track = SingingTrack(
            title="".join(event.name for event in track.title_parts),
            note_list=notes,
        )
        if self.options.import_pitch and (
            buffer := "".join(event.text for event in track.events if event.type == "metadata")
        ):
            pitch_data = VxPitchData.model_validate_json(buffer)
            pitch_points = [Point.start_point()]
            prev_pos = None
            for point in pitch_data.time_based_pitch_sequence.pitch_sequence:
                if prev_pos and point.position - prev_pos > 1 and pitch_points:
                    pitch_points.append(
                        Point(
                            x=pitch_points[-1].x,
                            y=-100,
                        )
                    )
                if pitch_points[-1].y == -100:
                    pitch_points.append(
                        Point(
                            x=int(
                                self.synchronizer.get_actual_ticks_from_secs(
                                    point.position
                                    * pitch_data.time_based_pitch_sequence.time_frame_period_seconds
                                )
                            )
                            + self.first_bar_length,
                            y=-100,
                        )
                    )
                pitch_points.append(
                    Point(
                        x=int(
                            self.synchronizer.get_actual_ticks_from_secs(
                                point.position
                                * pitch_data.time_based_pitch_sequence.time_frame_period_seconds
                            )
                        )
                        + self.first_bar_length,
                        y=int(point.pitch) + 6900,
                    )
                )
                prev_pos = point.position
            if len(pitch_points) > 1:
                pitch_points.append(
                    Point(
                        x=pitch_points[-1].x,
                        y=-100,
                    )
                )
            pitch_points.append(Point.end_point())
            singing_track.edited_params.pitch.points.root = pitch_points
        return singing_track

    def parse_tracks(self, vx_tracks: list[Annotated[Container, VxTrack]]) -> list[SingingTrack]:
        return [self.parse_track(track) for track in vx_tracks]
