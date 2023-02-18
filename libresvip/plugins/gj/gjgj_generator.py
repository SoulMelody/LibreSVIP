import dataclasses
from typing import List, Tuple

import mido

from libresvip.core.constants import TICKS_IN_BEAT
from libresvip.core.lyric_phoneme.chinese import get_pinyin_series
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import (
    InstrumentalTrack,
    Note,
    ParamCurve,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
    Track,
)

from .constants import SUPPORTED_PINYIN
from .model import (
    GjgjBeatItems,
    GjgjBeatStyle,
    GjgjInstrumentalTrack,
    GjgjPoint,
    GjgjProject,
    GjgjSingingTrack,
    GjgjTempoMap,
    GjgjTempos,
    GjgjTimeSignature,
    GjgjTone,
    GjgjTrackVolume,
    GjgjVolumeMap,
)
from .options import OutputOptions
from .singers import singer2id


@dataclasses.dataclass
class GjgjGenerator:
    options: OutputOptions
    max_note_id: int = dataclasses.field(init=False)
    first_numerator: int = dataclasses.field(init=False)
    first_bar_bpm: float = dataclasses.field(init=False)
    param_sample_interval: int = dataclasses.field(init=False)
    time_synchronizer: TimeSynchronizer = dataclasses.field(init=False)

    def generate_project(self, project: Project) -> GjgjProject:
        self.max_note_id = 1
        self.time_synchronizer = TimeSynchronizer(project.song_tempo_list)
        gjgj_project = GjgjProject(
            gjgjVersion=2,
            TempoMap=GjgjTempoMap(
                TicksPerQuarterNote=TICKS_IN_BEAT,
                Tempos=self.generate_tempos(project.song_tempo_list),
                TimeSignature=self.generate_time_signatures(
                    project.time_signature_list
                ),
            ),
        )
        gjgj_project.tracks, gjgj_project.accompaniments = self.generate_tracks(
            project.track_list
        )
        return gjgj_project

    def generate_tempos(self, song_tempo_list: List[SongTempo]) -> List[GjgjTempos]:
        self.first_bar_bpm = song_tempo_list[0].bpm
        return [
            GjgjTempos(
                MicrosecondsPerQuarterNote=mido.bpm2tempo(tempo.bpm),
                Time=tempo.position,
            )
            for tempo in song_tempo_list
        ]

    def generate_time_signatures(
        self, time_signature_list: List[TimeSignature]
    ) -> List[GjgjTimeSignature]:
        self.first_numerator = time_signature_list[0].numerator
        gjgj_time_signatures = []
        prev_ticks = 0
        for time_signature in time_signature_list:
            gjgj_time_signatures.append(
                GjgjTimeSignature(
                    Numerator=time_signature.numerator,
                    Denominator=time_signature.denominator,
                    Time=prev_ticks,
                )
            )
            prev_ticks += round(
                time_signature.bar_index * TICKS_IN_BEAT * time_signature.numerator
            )
        return gjgj_time_signatures

    def generate_tracks(
        self, track_list: List[Track]
    ) -> Tuple[List[GjgjSingingTrack], List[GjgjInstrumentalTrack]]:
        singing_tracks = []
        instrumental_tracks = []
        track_index = 1
        for track in track_list:
            if isinstance(track, SingingTrack):
                singing_tracks.append(self.generate_singing_track(track, track_index))
                track_index += 1
            elif isinstance(track, InstrumentalTrack):
                instrumental_tracks.append(
                    self.generate_instrumental_track(track, track_index)
                )
                track_index += 1
        return singing_tracks, instrumental_tracks

    def generate_singing_track(
        self, track: SingingTrack, track_index: int
    ) -> GjgjSingingTrack:
        gjgj_track = GjgjSingingTrack(
            ID=str(track_index),
            Name=singer2id[self.options.singer or track.ai_singer_name],
            MasterVolume=GjgjTrackVolume(Mute=track.mute),
            BeatItems=self.generate_notes(track.note_list),
            Tone=self.generate_pitch(track.edited_params.pitch),
            VolumeMap=self.generate_volume(track.edited_params.volume),
        )
        return gjgj_track

    def generate_instrumental_track(
        self, track: InstrumentalTrack, track_index: int
    ) -> GjgjInstrumentalTrack:
        gjgj_track = GjgjInstrumentalTrack(
            ID=str(track_index),
            Path=track.audio_file_path,
            Offset=self.position_to_time(track.offset),
            MasterVolume=GjgjTrackVolume(Mute=track.mute),
        )
        return gjgj_track

    def position_to_time(self, origin: int) -> int:
        position = origin + self.first_numerator * TICKS_IN_BEAT
        if position > 0:
            return round(
                self.time_synchronizer.get_actual_secs_from_ticks(position) * 10000000
            )
        else:
            return round(position / TICKS_IN_BEAT * 60 / self.first_bar_bpm * 10000000)

    def generate_notes(self, note_list: List[Note]) -> List[GjgjBeatItems]:
        notes = []
        pinyin_list = get_pinyin_series([note.lyric for note in note_list])
        for note, pinyin in zip(note_list, pinyin_list):
            if note.pronunciation is None:
                pronunciation = pinyin
            else:
                pronunciation = note.pronunciation
            if pronunciation not in SUPPORTED_PINYIN:
                pronunciation = ""
            if note.head_tag == "V":
                beat_style = GjgjBeatStyle.SP
            elif note.head_tag == "0":
                beat_style = GjgjBeatStyle.SIL
            else:
                beat_style = GjgjBeatStyle.NONE
            pre_time, post_time = 0, 0
            if note.edited_phones is not None:
                try:
                    if note.edited_phones.head_length_in_secs != -1:
                        note_start_pos_in_ticks = (
                            note.start_pos + self.first_numerator * TICKS_IN_BEAT
                        )
                        note_start_pos_in_secs = (
                            self.time_synchronizer.get_actual_secs_from_ticks(
                                note_start_pos_in_ticks
                            )
                        )
                        phone_head_position_in_secs = (
                            note_start_pos_in_secs
                            + note.edited_phones.head_length_in_secs
                        )
                        phone_head_position_in_ticks = (
                            self.time_synchronizer.get_actual_ticks_from_secs(
                                phone_head_position_in_secs
                            )
                        )
                        difference = (
                            note_start_pos_in_ticks - phone_head_position_in_ticks
                        )
                        pre_time = -difference * (2000 / 3) / TICKS_IN_BEAT

                    if note.edited_phones.mid_ratio_over_tail != -1:
                        post_time = (
                            -(
                                note.length
                                / (1 + note.edited_phones.mid_ratio_over_tail)
                            )
                            * (2000 / 3)
                            / TICKS_IN_BEAT
                        )
                except Exception:
                    pass
            notes.append(
                GjgjBeatItems(
                    ID=self.max_note_id,
                    Lyric=note.lyric,
                    Pinyin=pronunciation,
                    StartTick=note.start_pos + self.first_numerator * TICKS_IN_BEAT,
                    Duration=note.length,
                    Track=note.key_number,
                    Style=beat_style,
                    PreTime=pre_time,
                    PostTime=post_time,
                )
            )
            self.max_note_id += 1
        return notes

    def generate_pitch(self, pitch: ParamCurve) -> GjgjTone:
        ticks_buffer = []
        value_buffer = []
        ori_prev_ticks = -100
        pitch_points = []
        modify_ranges = []
        for point in pitch.points:
            ori_ticks, ori_value = point.x, point.y
            if ori_prev_ticks != ori_ticks:
                if ori_value != -100 and ori_ticks not in (-192000, 1073741823):
                    ticks_buffer.append(ori_ticks)
                    value_buffer.append(ori_value)
                elif len(ticks_buffer) > 0 and len(value_buffer) > 0:
                    for i in range(len(ticks_buffer)):
                        pitch_points.append(
                            GjgjPoint(
                                X=ticks_buffer[i],
                                Y=value_buffer[i],
                            )
                        )
                    modify_ranges.append(
                        GjgjPoint(
                            X=ticks_buffer[0],
                            Y=ticks_buffer[-1],
                        )
                    )
                    ticks_buffer = []
                    value_buffer = []
            ori_prev_ticks = ori_ticks
        gjgj_pitch = GjgjTone(
            Modifys=pitch_points,
            ModifyRanges=modify_ranges,
        )
        return gjgj_pitch

    def generate_volume(self, volume_curve: ParamCurve) -> List[GjgjVolumeMap]:
        volume_curve = volume_curve.reduce_sample_rate(self.options.down_sample)
        volume_map = []
        ticks_buffer = []
        value_buffer = []
        prev_ticks = 0
        for volume in volume_curve.points[1:]:
            tick = volume.x
            ori_value = volume.y
            value = (ori_value + 1000) / 1000
            if prev_ticks != tick:
                if ori_value != 0:
                    ticks_buffer.append(tick)
                    value_buffer.append(value)
                elif len(ticks_buffer) > 0 and len(value_buffer) > 0:
                    volume_map.append(
                        GjgjVolumeMap(
                            Time=ticks_buffer[0] - 5,
                            Volume=1,
                        )
                    )
                    for i in range(len(ticks_buffer)):
                        volume_map.append(
                            GjgjVolumeMap(
                                Time=ticks_buffer[i],
                                Volume=value_buffer[i],
                            )
                        )
                    volume_map.append(
                        GjgjVolumeMap(
                            Time=ticks_buffer[-1] + 5,
                            Volume=1,
                        )
                    )
                    ticks_buffer = []
                    value_buffer = []
        return volume_map
