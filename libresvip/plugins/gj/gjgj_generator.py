import contextlib
import dataclasses

import mido_fix as mido

from libresvip.core.constants import TICKS_IN_BEAT
from libresvip.core.lyric_phoneme.chinese import get_pinyin_series
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.core.warning_types import show_warning
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
from libresvip.utils.translation import gettext_lazy as _

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
from .singers import DEFAULT_SINGER_ID, singer2id


@dataclasses.dataclass
class GjgjGenerator:
    options: OutputOptions
    max_note_id: int = dataclasses.field(init=False)
    first_bar_length: int = dataclasses.field(init=False)
    first_bar_bpm: float = dataclasses.field(init=False)
    param_sample_interval: int = dataclasses.field(init=False)
    time_synchronizer: TimeSynchronizer = dataclasses.field(init=False)

    def generate_project(self, project: Project) -> GjgjProject:
        self.max_note_id = 1
        self.time_synchronizer = TimeSynchronizer(project.song_tempo_list)
        gjgj_project = GjgjProject(
            gjgj_version=2,
            tempo_map=GjgjTempoMap(
                ticks_per_quarter_note=TICKS_IN_BEAT,
                tempos=self.generate_tempos(project.song_tempo_list),
                time_signature=self.generate_time_signatures(project.time_signature_list),
            ),
        )
        gjgj_project.tracks, gjgj_project.accompaniments = self.generate_tracks(project.track_list)
        return gjgj_project

    def generate_tempos(self, song_tempo_list: list[SongTempo]) -> list[GjgjTempos]:
        self.first_bar_bpm = song_tempo_list[0].bpm
        return [
            GjgjTempos(
                microseconds_per_quarter_note=mido.bpm2tempo(tempo.bpm),
                time=tempo.position,
            )
            for tempo in song_tempo_list
        ]

    def generate_time_signatures(
        self, time_signature_list: list[TimeSignature]
    ) -> list[GjgjTimeSignature]:
        self.first_bar_length = int(time_signature_list[0].bar_length())
        gjgj_time_signatures = []
        prev_ticks = 0
        for time_signature in time_signature_list:
            gjgj_time_signatures.append(
                GjgjTimeSignature(
                    numerator=time_signature.numerator,
                    denominator=time_signature.denominator,
                    time=prev_ticks,
                )
            )
            prev_ticks += round(time_signature.bar_index * time_signature.bar_length())
        return gjgj_time_signatures

    def generate_tracks(
        self, track_list: list[Track]
    ) -> tuple[list[GjgjSingingTrack], list[GjgjInstrumentalTrack]]:
        singing_tracks = []
        instrumental_tracks = []
        track_index = 1
        for track in track_list:
            if isinstance(track, SingingTrack):
                singing_tracks.append(self.generate_singing_track(track, track_index))
                track_index += 1
            elif isinstance(track, InstrumentalTrack):
                instrumental_tracks.append(self.generate_instrumental_track(track, track_index))
                track_index += 1
        return singing_tracks, instrumental_tracks

    def generate_singing_track(self, track: SingingTrack, track_index: int) -> GjgjSingingTrack:
        return GjgjSingingTrack(
            id_value=str(track_index),
            name=singer2id.get(self.options.singer or track.ai_singer_name, DEFAULT_SINGER_ID),
            master_volume=GjgjTrackVolume(mute=track.mute),
            beat_items=self.generate_notes(track.note_list),
            tone=self.generate_pitch(track.edited_params.pitch),
            volume_map=self.generate_volume(track.edited_params.volume),
        )

    def generate_instrumental_track(
        self, track: InstrumentalTrack, track_index: int
    ) -> GjgjInstrumentalTrack:
        return GjgjInstrumentalTrack(
            id_value=str(track_index),
            path=track.audio_file_path,
            offset=self.position_to_time(track.offset),
            master_volume=GjgjTrackVolume(mute=track.mute),
        )

    def position_to_time(self, position: int) -> int:
        if position > 0:
            return round(self.time_synchronizer.get_actual_secs_from_ticks(position) * 10000000)
        else:
            return round(position / TICKS_IN_BEAT * 60 / self.first_bar_bpm * 10000000)

    def generate_notes(self, note_list: list[Note]) -> list[GjgjBeatItems]:
        notes = []
        pinyin_list = get_pinyin_series([note.lyric for note in note_list])
        for note, pinyin in zip(note_list, pinyin_list):
            pronunciation = note.pronunciation or pinyin
            if pronunciation not in SUPPORTED_PINYIN:
                msg_prefx = _("Unsupported pinyin:")
                show_warning(f"{msg_prefx} {pronunciation}")
                pronunciation = ""
            if note.head_tag == "0":
                beat_style = GjgjBeatStyle.SIL
            elif note.head_tag == "V":
                beat_style = GjgjBeatStyle.SP
            else:
                beat_style = GjgjBeatStyle.NONE
            pre_time, post_time = 0.0, 0.0
            if note.edited_phones is not None:
                with contextlib.suppress(Exception):
                    if note.edited_phones.head_length_in_secs != -1:
                        note_start_pos_in_ticks = note.start_pos
                        note_start_pos_in_secs = self.time_synchronizer.get_actual_secs_from_ticks(
                            note_start_pos_in_ticks
                        )
                        phone_head_position_in_secs = (
                            note_start_pos_in_secs + note.edited_phones.head_length_in_secs
                        )
                        phone_head_position_in_ticks = (
                            self.time_synchronizer.get_actual_ticks_from_secs(
                                phone_head_position_in_secs
                            )
                        )
                        difference = note_start_pos_in_ticks - phone_head_position_in_ticks
                        pre_time = -difference * (2000 / 3) / TICKS_IN_BEAT

                    if note.edited_phones.mid_ratio_over_tail != -1:
                        post_time = (
                            -(note.length / (1 + note.edited_phones.mid_ratio_over_tail))
                            * (2000 / 3)
                            / TICKS_IN_BEAT
                        )
            notes.append(
                GjgjBeatItems(
                    id_value=self.max_note_id,
                    lyric=note.lyric,
                    pinyin=pronunciation,
                    start_tick=note.start_pos + self.first_bar_length,
                    duration=note.length,
                    track=note.key_number,
                    style=beat_style,
                    pre_time=pre_time,
                    post_time=post_time,
                )
            )
            self.max_note_id += 1
        return notes

    def generate_pitch(self, pitch: ParamCurve) -> GjgjTone:
        ticks_buffer = []
        value_buffer = []
        ori_prev_ticks = -100
        pitch_points: list[GjgjPoint] = []
        modify_ranges = []
        for point in pitch.points.root:
            ori_ticks, ori_value = point.x, point.y
            if ori_prev_ticks != ori_ticks:
                if ori_value != -100 and ori_ticks not in (
                    -192000,
                    1073741823,
                ):
                    ticks_buffer.append(ori_ticks - self.first_bar_length)
                    value_buffer.append(ori_value)
                elif len(ticks_buffer) > 0 and len(value_buffer) > 0:
                    pitch_points.extend(
                        GjgjPoint(
                            x=ticks_buffer[i],
                            y=value_buffer[i],
                        )
                        for i in range(len(ticks_buffer))
                    )
                    modify_ranges.append(
                        GjgjPoint(
                            x=ticks_buffer[0],
                            y=ticks_buffer[-1],
                        )
                    )
                    ticks_buffer.clear()
                    value_buffer.clear()
            ori_prev_ticks = ori_ticks
        return GjgjTone(
            modifies=pitch_points,
            modify_ranges=modify_ranges,
        )

    def generate_volume(self, volume_curve: ParamCurve) -> list[GjgjVolumeMap]:
        volume_curve = volume_curve.reduce_sample_rate(self.options.down_sample)
        volume_map = []
        ticks_buffer = []
        value_buffer = []
        prev_ticks = 0
        for volume in volume_curve.points.root[1:]:
            tick = volume.x
            if prev_ticks != tick:
                ori_value = volume.y
                value = (ori_value + 1000) / 1000
                if ori_value != 0:
                    ticks_buffer.append(tick - self.first_bar_length)
                    value_buffer.append(value)
                elif len(ticks_buffer) > 0 and len(value_buffer) > 0:
                    volume_map.append(
                        GjgjVolumeMap(
                            time=ticks_buffer[0] - 5,
                            volume=1,
                        )
                    )
                    volume_map.extend(
                        GjgjVolumeMap(
                            time=ticks_buffer[i],
                            volume=value_buffer[i],
                        )
                        for i in range(len(ticks_buffer))
                    )
                    volume_map.append(
                        GjgjVolumeMap(
                            time=ticks_buffer[-1] + 5,
                            volume=1,
                        )
                    )
                    ticks_buffer.clear()
                    value_buffer.clear()
        return volume_map
