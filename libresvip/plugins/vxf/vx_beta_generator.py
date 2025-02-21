import dataclasses
import operator
from typing import Any

import more_itertools

from libresvip.core.constants import TICKS_IN_BEAT
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import Project, SingingTrack, SongTempo, TimeSignature, Track

from .model import VxPitchData, VxPitchPoint, VxTimeBasedPitchSequence
from .options import OutputOptions

Container = dict[str, Any]


@dataclasses.dataclass
class VxBetaGenerator:
    options: OutputOptions
    synchronizer: TimeSynchronizer = dataclasses.field(init=False)
    first_bar_length: int = dataclasses.field(init=False)

    @property
    def tick_rate(self) -> float:
        return TICKS_IN_BEAT / self.options.ticks_per_beat

    def generate_project(self, project: Project) -> Container:
        self.first_bar_length = round(
            project.time_signature_list[0].bar_length(self.options.ticks_per_beat)
        )
        self.synchronizer = TimeSynchronizer(project.song_tempo_list)
        master_track_events = []
        master_track_events.extend(self.generate_tempos(project.song_tempo_list))
        master_track_events.extend(self.generate_time_signatures(project.time_signature_list))
        if tracks := self.generate_tracks(project.track_list):
            tracks[0]["events"].extend(master_track_events)
        self._convert_cumulative_to_delta(tracks)
        return {
            "ticks_per_beat": self.options.ticks_per_beat,
            "tracks": tracks,
        }

    @staticmethod
    def _convert_cumulative_to_delta(tracks: list[Container]) -> None:
        for track in tracks:
            tick = 0
            track["events"] = sorted(track["events"], key=operator.itemgetter("time"))
            for event in track["events"]:
                tick, event["time"] = event["time"], event["time"] - tick

    def generate_tempos(self, song_tempo_list: list[SongTempo]) -> list[Container]:
        return [
            {
                "tempo": tempo.bpm,
                "time": round(tempo.position / self.tick_rate),
            }
            for tempo in song_tempo_list
            if tempo.position >= 0
        ]

    def generate_time_signatures(
        self,
        time_signature_list: list[TimeSignature],
    ) -> list[Container]:
        events = []
        prev_ticks = 0
        prev_time_signature = None
        for time_signature in time_signature_list:
            if time_signature.bar_index >= 0:
                if prev_time_signature is not None:
                    prev_ticks += round(
                        (time_signature.bar_index - prev_time_signature.bar_index)
                        * prev_time_signature.bar_length(self.options.ticks_per_beat)
                    )
                events.append(
                    {
                        "numerator": time_signature.numerator,
                        "denominator": time_signature.denominator,
                        "time": prev_ticks,
                    }
                )
                prev_time_signature = time_signature
        return events

    def generate_tracks(self, tracks: list[Track]) -> list[Container]:
        return [
            mido_track
            for track in tracks
            if isinstance(track, SingingTrack)
            and (mido_track := self.generate_track(track)) is not None
        ]

    def generate_track(self, track: SingingTrack) -> Container | None:
        events: list[Container] = []
        encoded_title = track.title.encode().decode("latin-1")
        title_parts = []
        for is_first, is_last, i in more_itertools.mark_ends(range(0, len(encoded_title), 12)):
            if len(encoded_title) <= 12:
                title_parts.append(
                    {"name": encoded_title[i : i + 12].encode("latin-1").decode(), "seq_stat": 0x10}
                )
            elif is_first:
                title_parts.append(
                    {"name": encoded_title[i : i + 12].encode("latin-1").decode(), "seq_stat": 0x50}
                )
            elif is_last:
                title_parts.append(
                    {"name": encoded_title[i : i + 12].encode("latin-1").decode(), "seq_stat": 0xD0}
                )
            else:
                title_parts.append(
                    {"name": encoded_title[i : i + 12].encode("latin-1").decode(), "seq_stat": 0x90}
                )
        for i, note in enumerate(track.note_list):
            lyric = "l-aa"
            if note.lyric.isascii():
                lyric = note.lyric
            elif note.pronunciation and note.pronunciation.isascii():
                lyric = note.pronunciation
            if lyric:
                for is_first, is_last, offset in more_itertools.mark_ends(
                    range(-2, len(lyric), 12)
                ):
                    if len(lyric) <= 10:
                        events.append(
                            {
                                "type": "lyrics",
                                "seq_num": i,
                                "seq_stat": 0x10,
                                "text": lyric[:10],
                                "time": 0,
                            }
                        )
                    elif is_first:
                        events.append(
                            {
                                "type": "lyrics",
                                "seq_num": i,
                                "seq_stat": 0x50,
                                "text": lyric[:10],
                                "time": 0,
                            }
                        )
                    elif is_last:
                        events.append(
                            {
                                "type": "lyrics",
                                "seq_num": None,
                                "seq_stat": 0xD0,
                                "text": lyric[offset:],
                                "time": 0,
                            }
                        )
                    else:
                        events.append(
                            {
                                "type": "lyrics",
                                "seq_num": None,
                                "seq_stat": 0x90,
                                "text": lyric[offset : offset + 12],
                                "time": 0,
                            }
                        )
            events.extend(
                [
                    {
                        "type": "note_on",
                        "note": note.key_number,
                        "time": round(note.start_pos / self.tick_rate),
                        "velocity": 0x7F,
                        "on_data": i,
                    },
                    {
                        "type": "note_off",
                        "note": note.key_number,
                        "time": round(note.end_pos / self.tick_rate),
                        "velocity": 0x00,
                        "off_data": 0x00,
                    },
                ]
            )
        prev_point = None
        secs_step = 1 / 200
        pitch_data = VxPitchData(
            time_based_pitch_sequence=VxTimeBasedPitchSequence(
                time_frame_period_seconds=secs_step,
            )
        )
        for pitch_point in track.edited_params.pitch.points.root:
            if pitch_point.y != -100:
                pos = int(
                    self.synchronizer.get_actual_secs_from_ticks(
                        pitch_point.x - self.first_bar_length
                    )
                    / secs_step
                )
                if prev_point is not None:
                    pitch_data.time_based_pitch_sequence.pitch_sequence.extend(
                        [
                            VxPitchPoint(
                                position=interp_pos,
                                pitch=(
                                    prev_point.pitch
                                    + (pitch_point.y - 6900 - prev_point.pitch)
                                    * (
                                        (interp_pos - prev_point.position)
                                        / (pos - prev_point.position)
                                    )
                                )
                                if interp_pos != pos
                                else pitch_point.y - 6900,
                            )
                            for interp_pos in range(prev_point.position + 1, pos + 1)
                        ]
                    )
                else:
                    pitch_data.time_based_pitch_sequence.pitch_sequence.append(
                        VxPitchPoint(position=pos, pitch=pitch_point.y - 6900)
                    )
                prev_point = pitch_data.time_based_pitch_sequence.pitch_sequence[-1]
            else:
                prev_point = None
            if pitch_data.time_based_pitch_sequence.pitch_sequence:
                pitch_data.time_based_pitch_sequence.num_frames_overall_sequence = (
                    pitch_data.time_based_pitch_sequence.pitch_sequence[-1].position
                )
        pitch_data_json = pitch_data.model_dump_json(by_alias=True)
        for is_first, is_last, offset in more_itertools.mark_ends(
            range(0, len(pitch_data_json), 12)
        ):
            if len(pitch_data_json) <= 12:
                events.append(
                    {
                        "type": "metadata",
                        "text": pitch_data_json[:12],
                        "time": 0,
                    }
                )
            elif is_first:
                events.append(
                    {
                        "type": "metadata",
                        "seq_stat": 0x50,
                        "text": pitch_data_json[:12],
                        "time": 0,
                    }
                )
            elif is_last:
                events.append(
                    {
                        "type": "metadata",
                        "seq_stat": 0xD0,
                        "text": pitch_data_json[offset:],
                        "time": 0,
                    }
                )
            else:
                events.append(
                    {
                        "type": "metadata",
                        "seq_stat": 0x90,
                        "text": pitch_data_json[offset : offset + 12],
                        "time": 0,
                    }
                )
        if events:
            return {"title_parts": title_parts, "events": events}
