import dataclasses
import math

import mido

from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import (
    InstrumentalTrack,
    Note,
    ParamCurve,
    Params,
    Phones,
    Point,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
    Track,
)
from libresvip.utils import find_index

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
from .singers import id2singer


@dataclasses.dataclass
class GjgjParser:
    options: InputOptions
    time_synchronizer: TimeSynchronizer = dataclasses.field(init=False)
    first_bar_length: int = dataclasses.field(init=False)
    ticks_in_beat: int = dataclasses.field(init=False)

    def parse_project(self, gjgj_project: GjgjProject) -> Project:
        self.ticks_in_beat = gjgj_project.tempo_map.ticks_per_quarter_note
        project = Project(
            SongTempoList=self.parse_tempos(gjgj_project.tempo_map),
            TimeSignatureList=self.parse_time_signatures(
                gjgj_project.tempo_map.time_signature
            ),
        )
        project.track_list = self.parse_singing_tracks(gjgj_project.tracks)
        project.track_list.extend(
            self.parse_instrumental_tracks(gjgj_project.accompaniments)
        )
        return project

    def parse_tempos(self, tempo_map: GjgjTempoMap) -> list[SongTempo]:
        tempos = []
        for tempo in tempo_map.tempos:
            tempos.append(
                SongTempo(
                    Position=tempo.time,
                    BPM=mido.tempo2bpm(tempo.microseconds_per_quarter_note),
                )
            )
        self.time_synchronizer = TimeSynchronizer(tempos)
        return tempos

    def parse_time_signatures(
        self, time_signatures: list[GjgjTimeSignature]
    ) -> list[TimeSignature]:
        if not len(time_signatures) or time_signatures[0].time != 0:
            time_signatures.insert(
                0, GjgjTimeSignature(Time=0, Numerator=4, Denominator=4)
            )
        time_signature_changes = [
            TimeSignature(
                BarIndex=0,
                Numerator=time_signatures[0].numerator,
                Denominator=time_signatures[0].denominator,
            )
        ]
        self.first_bar_length = (self.ticks_in_beat * 4) * time_signatures[0].numerator / time_signatures[0].denominator

        prev_ticks = 0
        measure = 0
        for time_signature in time_signatures[1:]:
            tick_in_full_note = (
                self.ticks_in_beat * time_signature_changes[-1].numerator
            )
            tick = time_signature.time
            measure += (tick - prev_ticks) / tick_in_full_note
            ts_obj = TimeSignature(
                BarIndex=math.floor(measure),
                Numerator=time_signature.numerator,
                Denominator=time_signature.denominator,
            )
            time_signature_changes.append(ts_obj)
            prev_ticks = tick
        return time_signature_changes

    def parse_singing_tracks(self, tracks: list[GjgjSingingTrack]) -> list[Track]:
        return [
            SingingTrack(
                AISingerName=id2singer[track.singer_info.display_name],
                Mute=track.master_volume.mute,
                NoteList=self.parse_notes(track.beat_items),
                EditedParams=self.parse_params(track),
            )
            for track in tracks
        ]

    def parse_instrumental_tracks(
        self, accompaniments: list[GjgjInstrumentalTrack]
    ) -> list[Track]:
        return [
            InstrumentalTrack(
                Mute=accompaniment.master_volume.mute,
                AudioFilePath=accompaniment.path,
                Offset=round(
                    self.time_synchronizer.get_actual_ticks_from_secs(
                        accompaniment.offset / 10000000
                    )
                    - self.first_bar_length
                ),
            )
            for accompaniment in accompaniments
        ]

    def parse_notes(self, beat_items: list[GjgjBeatItems]) -> list[Note]:
        note_list = []
        for beat_item in beat_items:
            start_pos = beat_item.start_tick - self.first_bar_length
            note = Note(
                StartPos=start_pos,
                Length=beat_item.duration,
                Lyric=beat_item.lyric.strip(),
                KeyNumber=beat_item.track,
                Pronunciation=beat_item.pinyin,
                EditedPhones=self.parse_phones(beat_item, start_pos),
            )
            if beat_item.style == GjgjBeatStyle.SP:
                note.head_tag = "V"
            elif beat_item.style == GjgjBeatStyle.SIL:
                note.head_tag = "0"
            note_list.append(note)
        return note_list

    def parse_phones(self, beat_item: GjgjBeatItems, start_pos: int) -> Phones:
        phones = Phones()
        try:
            if beat_item.pre_time != 0:
                difference = round(beat_item.pre_time * 480 * 3 / 2000)
                if difference > 0:
                    phones.head_length_in_secs = (
                        self.time_synchronizer.get_actual_secs_from_ticks(start_pos)
                        - self.time_synchronizer.get_actual_secs_from_ticks(difference)
                    )
                else:
                    phones.head_length_in_secs = -1
            if beat_item.post_time != 0:
                essential_vowel_length = (
                    beat_item.duration * (2000 / 3) / 480 + beat_item.post_time
                )
                tail_vowel_length = -beat_item.post_time
                phones.mid_ratio_over_tail = essential_vowel_length / tail_vowel_length
            else:
                phones.mid_ratio_over_tail = -1
        except Exception:
            pass
        return phones

    def parse_params(self, track: GjgjSingingTrack) -> Params:
        params = Params(
            Pitch=self.parse_pitch_curve(track.tone),
            Volume=self.parse_volume_curve(track.volume_map),
        )
        return params

    @staticmethod
    def pitch_time_to_position(pitch_time: float) -> int:
        return round(pitch_time * 5)

    def parse_pitch_curve(self, tone: GjgjTone) -> ParamCurve:
        pitch_curve = ParamCurve()
        pitch_curve.points.append(Point.start_point())
        try:
            for mod_range in tone.modify_ranges:
                left_point = Point(self.pitch_time_to_position(mod_range.x), -100)
                right_point = Point(self.pitch_time_to_position(mod_range.y), -100)
                index = find_index(
                    tone.modifies, lambda p: (mod_range.x <= p.time <= mod_range.y)
                )
                if index == -1:
                    continue
                pitch_curve.points.append(left_point)
                while (
                    index < len(tone.modifies) and tone.modifies[index].x <= mod_range.y
                ):
                    pitch_curve.points.append(
                        Point(
                            self.pitch_time_to_position(tone.modifies[index].x),
                            self.pitch_time_to_position(tone.modifies[index].y),
                        )
                    )
                    index += 1
                pitch_curve.points.append(right_point)
        except Exception:
            pass
        pitch_curve.points.append(Point.end_point())
        return pitch_curve

    def parse_volume_curve(self, volume_map: list[GjgjVolumeMap]) -> ParamCurve:
        volume_curve = ParamCurve()
        volume_curve.points = [
            Point(round(volume_item.time), round(volume_item.volume))
            for volume_item in volume_map
        ]
        return volume_curve
