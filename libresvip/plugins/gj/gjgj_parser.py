import contextlib
import dataclasses
import math

import mido_fix as mido

from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import (
    InstrumentalTrack,
    Note,
    ParamCurve,
    Params,
    Phones,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
    Track,
)
from libresvip.model.point import Point
from libresvip.utils.search import find_index

from .model import (
    GjgjBeatItems,
    GjgjBeatStyle,
    GjgjInstrumentalTrack,
    GjgjProject,
    GjgjSingingTrack,
    GjgjTempoMap,
    GjgjTimeSignature,
    GjgjTone,
    GjgjVolumeMap,
)
from .options import InputOptions
from .singers import DEFAULT_SINGER, id2singer


@dataclasses.dataclass
class GjgjParser:
    options: InputOptions
    time_synchronizer: TimeSynchronizer = dataclasses.field(init=False)
    first_bar_length: int = dataclasses.field(init=False)
    ticks_in_beat: int = dataclasses.field(init=False)

    def parse_project(self, gjgj_project: GjgjProject) -> Project:
        self.ticks_in_beat = gjgj_project.tempo_map.ticks_per_quarter_note
        project = Project(
            song_tempo_list=self.parse_tempos(gjgj_project.tempo_map),
            time_signature_list=self.parse_time_signatures(gjgj_project.tempo_map.time_signature),
        )
        project.track_list = self.parse_singing_tracks(gjgj_project.tracks)
        if self.options.import_instrumental_track:
            project.track_list.extend(self.parse_instrumental_tracks(gjgj_project.accompaniments))
        return project

    def parse_tempos(self, tempo_map: GjgjTempoMap) -> list[SongTempo]:
        tempos = [
            SongTempo(
                position=tempo.time,
                bpm=mido.tempo2bpm(tempo.microseconds_per_quarter_note),
            )
            for tempo in tempo_map.tempos
        ]
        self.time_synchronizer = TimeSynchronizer(tempos)
        return tempos

    def parse_time_signatures(
        self, time_signatures: list[GjgjTimeSignature]
    ) -> list[TimeSignature]:
        if not len(time_signatures) or time_signatures[0].time != 0:
            time_signatures.insert(0, GjgjTimeSignature(time=0, numerator=4, denominator=4))
        time_signature_changes = [
            TimeSignature(
                bar_index=0,
                numerator=time_signatures[0].numerator,
                denominator=time_signatures[0].denominator,
            )
        ]
        self.first_bar_length = int(time_signature_changes[0].bar_length(self.ticks_in_beat))

        prev_ticks = 0
        measure = 0.0
        for time_signature in time_signatures[1:]:
            tick = time_signature.time
            measure += (tick - prev_ticks) / time_signature_changes[-1].bar_length(
                self.ticks_in_beat
            )
            ts_obj = TimeSignature(
                bar_index=math.floor(measure),
                numerator=time_signature.numerator,
                denominator=time_signature.denominator,
            )
            time_signature_changes.append(ts_obj)
            prev_ticks = tick
        return time_signature_changes

    def parse_singing_tracks(self, tracks: list[GjgjSingingTrack]) -> list[Track]:
        return [
            SingingTrack(
                ai_singer_name=id2singer.get(track.singer_info.display_name, DEFAULT_SINGER),
                mute=track.master_volume.mute if track.master_volume is not None else False,
                note_list=self.parse_notes(track.beat_items),
                edited_params=self.parse_params(track),
            )
            for track in tracks
        ]

    def parse_instrumental_tracks(self, accompaniments: list[GjgjInstrumentalTrack]) -> list[Track]:
        return [
            InstrumentalTrack(
                mute=accompaniment.master_volume.mute
                if accompaniment.master_volume is not None
                else False,
                audio_file_path=accompaniment.path,
                offset=round(
                    self.time_synchronizer.get_actual_ticks_from_secs(
                        accompaniment.offset / 10000000
                    )
                ),
            )
            for accompaniment in accompaniments
        ]

    def parse_notes(self, beat_items: list[GjgjBeatItems]) -> list[Note]:
        note_list = []
        for beat_item in beat_items:
            start_pos = beat_item.start_tick
            note = Note(
                start_pos=start_pos,
                length=beat_item.duration,
                lyric=beat_item.lyric.strip(),
                key_number=beat_item.track,
                pronunciation=beat_item.pinyin,
                edited_phones=self.parse_phones(beat_item, start_pos),
            )
            if beat_item.style == GjgjBeatStyle.SP:
                note.head_tag = "V"
            elif beat_item.style == GjgjBeatStyle.SIL:
                note.head_tag = "0"
            note_list.append(note)
        return note_list

    def parse_phones(self, beat_item: GjgjBeatItems, start_pos: int) -> Phones:
        phones = Phones()
        with contextlib.suppress(Exception):
            if beat_item.pre_time != 0:
                difference = round(beat_item.pre_time * 480 * 3 / 2000)
                if difference > 0:
                    phones.head_length_in_secs = self.time_synchronizer.get_actual_secs_from_ticks(
                        start_pos
                    ) - self.time_synchronizer.get_actual_secs_from_ticks(difference)
                else:
                    phones.head_length_in_secs = -1
            if beat_item.post_time != 0:
                essential_vowel_length = beat_item.duration * (2000 / 3) / 480 + beat_item.post_time
                tail_vowel_length = -beat_item.post_time
                phones.mid_ratio_over_tail = essential_vowel_length / tail_vowel_length
            else:
                phones.mid_ratio_over_tail = -1
        return phones

    def parse_params(self, track: GjgjSingingTrack) -> Params:
        params = Params()
        if self.options.import_pitch:
            params.pitch = self.parse_pitch_curve(track.tone)
        if self.options.import_volume:
            params.volume = self.parse_volume_curve(track.volume_map)
        return params

    def pitch_time_to_position(self, pitch_time: float) -> int:
        return round(pitch_time * 5) + self.first_bar_length

    def parse_pitch_curve(self, tone: GjgjTone) -> ParamCurve:
        pitch_curve = ParamCurve()
        pitch_curve.points.append(Point.start_point())
        with contextlib.suppress(Exception):
            for mod_range in tone.modify_ranges:
                left_point = Point(self.pitch_time_to_position(mod_range.x), -100)
                right_point = Point(self.pitch_time_to_position(mod_range.y), -100)
                index = find_index(
                    tone.modifies,
                    lambda p: (mod_range.x <= p.time <= mod_range.y),
                )
                if index == -1:
                    continue
                pitch_curve.points.append(left_point)
                while index < len(tone.modifies) and tone.modifies[index].x <= mod_range.y:
                    pitch_curve.points.append(
                        Point(
                            self.pitch_time_to_position(tone.modifies[index].x),
                            self.pitch_time_to_position(tone.modifies[index].y),
                        )
                    )
                    index += 1
                pitch_curve.points.append(right_point)
        pitch_curve.points.append(Point.end_point())
        return pitch_curve

    def parse_volume_curve(self, volume_map: list[GjgjVolumeMap]) -> ParamCurve:
        volume_curve = ParamCurve()
        volume_curve.points.root = [
            Point(round(volume_item.time), round(volume_item.volume)) for volume_item in volume_map
        ]
        return volume_curve
