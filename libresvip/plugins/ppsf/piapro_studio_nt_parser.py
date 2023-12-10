import dataclasses
import functools
from typing import Optional

import more_itertools
import portion

from libresvip.core.time_interval import PiecewiseIntervalDict
from libresvip.model.base import (
    InstrumentalTrack,
    Note,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
)
from libresvip.model.point import Point, cosine_easing_in_interpolation

from .model import (
    PpsfAudioTrackItem,
    PpsfCurveType,
    PpsfDvlTrackEvent,
    PpsfDvlTrackItem,
    PpsfMeters,
    PpsfProject,
    PpsfTempos,
)
from .options import InputOptions


@dataclasses.dataclass
class PiaproStudioNTParser:
    options: InputOptions
    first_bar_ticks: int = dataclasses.field(init=False)

    def parse_project(self, ppsf_project: PpsfProject) -> Project:
        time_signatures = self.parse_time_signatures(ppsf_project.ppsf.project.meter)
        self.first_bar_ticks = round(time_signatures[0].bar_length())
        tempos = self.parse_tempos(ppsf_project.ppsf.project.tempo)
        singing_tracks = self.parse_singing_tracks(ppsf_project.ppsf.project.dvl_track)
        instrumental_tracks = self.parse_instrumental_tracks(
            ppsf_project.ppsf.project.audio_track
        )
        return Project(
            time_signature_list=time_signatures,
            song_tempo_list=tempos,
            track_list=singing_tracks + instrumental_tracks,
        )

    def parse_time_signatures(self, ppsf_meters: PpsfMeters) -> list[TimeSignature]:
        time_signatures = []
        first_time_signature = TimeSignature(
            numerator=ppsf_meters.const.nume,
            denominator=ppsf_meters.const.denomi,
        )
        if ppsf_meters.use_sequence:
            time_signatures.extend(
                TimeSignature(
                    numerator=meter.nume,
                    denominator=meter.denomi,
                    bar_index=meter.measure,
                )
                for meter in ppsf_meters.sequence
            )
        if not len(time_signatures) or time_signatures[0].bar_index != 0:
            time_signatures.insert(0, first_time_signature)
        return time_signatures

    def parse_tempos(self, ppsf_tempos: PpsfTempos) -> list[SongTempo]:
        tempos = []
        first_tempo = SongTempo(bpm=ppsf_tempos.const / 10000, position=0)
        if ppsf_tempos.use_sequence:
            tempos.extend(
                SongTempo(bpm=tempo.value / 10000, position=tempo.tick)
                for tempo in ppsf_tempos.sequence
            )
        if not len(tempos) or tempos[0].position != 0:
            tempos.insert(0, first_tempo)
        return tempos

    @staticmethod
    def base_key_interval_dict(track: SingingTrack) -> PiecewiseIntervalDict:
        interval_dict = PiecewiseIntervalDict()
        if len(track.note_list) == 1:
            interval_dict[portion.closedopen(0, portion.inf)] = track.note_list[
                0
            ].key_number
        else:
            for is_first, is_last, (prev_note, next_note) in more_itertools.mark_ends(
                more_itertools.pairwise(track.note_list)
            ):
                if is_first:
                    interval_dict[
                        portion.closedopen(0, prev_note.start_pos)
                    ] = prev_note.key_number
                if prev_note.length > 120:
                    interval_dict[
                        portion.closedopen(prev_note.start_pos, prev_note.end_pos - 120)
                    ] = prev_note.key_number
                    pitch_pos = prev_note.end_pos - 120
                else:
                    pitch_pos = prev_note.start_pos
                if next_note.start_pos - pitch_pos <= 480:
                    interval_dict[
                        portion.closedopen(pitch_pos, next_note.start_pos)
                    ] = functools.partial(
                        cosine_easing_in_interpolation,
                        start=Point(x=pitch_pos, y=prev_note.key_number),
                        end=Point(x=next_note.start_pos, y=next_note.key_number),
                    )
                else:
                    interval_dict[
                        portion.closedopen(
                            pitch_pos, (prev_note.end_pos + next_note.start_pos) // 2
                        )
                    ] = prev_note.key_number
                    interval_dict[
                        portion.closedopen(
                            (prev_note.end_pos + next_note.start_pos) // 2,
                            next_note.start_pos,
                        )
                    ] = next_note.key_number
                if is_last:
                    interval_dict[
                        portion.closedopen(next_note.start_pos, portion.inf)
                    ] = next_note.key_number
        return interval_dict

    def parse_instrumental_tracks(
        self, ppsf_audio_tracks: list[PpsfAudioTrackItem]
    ) -> list[InstrumentalTrack]:
        tracks = []
        for track in ppsf_audio_tracks:
            for i, event in enumerate(track.events):
                instrumental_track = InstrumentalTrack(
                    title=f"{track.name} {i + 1}",
                    audio_file_path=event.file_audio_data.file_path,
                    offset=event.tick_pos,
                )
                tracks.append(instrumental_track)
        return tracks

    def parse_singing_tracks(
        self, ppsf_dvl_tracks: Optional[list[PpsfDvlTrackItem]]
    ) -> list[SingingTrack]:
        tracks = []
        if ppsf_dvl_tracks is not None:
            for track in ppsf_dvl_tracks:
                singing_track = SingingTrack(
                    title=track.name,
                    ai_singer_name=track.singer.singer_name,
                    note_list=self.parse_notes(track.events),
                )
                for parameter in track.parameters:
                    if parameter.base_sequence.name == "pitch_bend":
                        key_interval_dict = self.base_key_interval_dict(singing_track)
                        for point in parameter.base_sequence.sequence:
                            if (
                                point.curve_type == PpsfCurveType.BORDER
                                and point.value == 0
                            ):
                                singing_track.edited_params.pitch.points.append(
                                    Point(
                                        x=point.pos + self.first_bar_ticks,
                                        y=-100,
                                    )
                                )
                            elif (
                                base_key := key_interval_dict.get(point.pos)
                            ) is not None:
                                singing_track.edited_params.pitch.points.append(
                                    Point(
                                        x=point.pos + self.first_bar_ticks,
                                        y=point.value + round(base_key * 100),
                                    )
                                )
                tracks.append(singing_track)
        return tracks

    def parse_notes(self, ppsf_dvl_track_events: list[PpsfDvlTrackEvent]) -> list[Note]:
        return [
            Note(
                key_number=event.note_number,
                start_pos=event.pos,
                length=event.length,
                lyric=event.lyric,
                pronunciation=event.symbols,
            )
            for event in ppsf_dvl_track_events
            if event.enabled
        ]
