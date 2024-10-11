import bisect
import dataclasses
from typing import Union

from libresvip.core.constants import DEFAULT_PHONEME
from libresvip.core.lyric_phoneme.chinese import CHINESE_RE, get_pinyin_series
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
from libresvip.utils.audio import audio_track_info

from .model import (
    AISAudioPattern,
    AISAudioTrack,
    AISNote,
    AISProjectBody,
    AISProjectHead,
    AISSingVoicePattern,
    AISSingVoiceTrack,
    AISTempo,
    AISTimeSignature,
)
from .options import OutputOptions


@dataclasses.dataclass
class AiSingersGenerator:
    options: OutputOptions
    synchronizer: TimeSynchronizer = dataclasses.field(init=False)
    first_bar_length: int = dataclasses.field(init=False)

    def generate_project(self, project: Project) -> tuple[AISProjectHead, AISProjectBody]:
        self.synchronizer = TimeSynchronizer(project.song_tempo_list)
        self.first_bar_length = round(project.time_signature_list[0].bar_length())
        ais_time_signatures = self.generate_time_signatures(project.time_signature_list)
        ais_tempos = self.generate_tempos(project.song_tempo_list, project.time_signature_list)
        max_end_time = round(
            max(
                (
                    note.end_pos
                    for track in project.track_list
                    if isinstance(track, SingingTrack)
                    for note in track.note_list
                ),
                default=project.song_tempo_list[-1].position,
            )
            / 15
        )
        num_bars = ais_tempos[-1].start_bar + (max_end_time - ais_tempos[-1].start_128) // (
            128 * ais_time_signatures[-1].beat_zi / ais_time_signatures[-1].beat_mu
        )
        ais_project_head = AISProjectHead(
            signature=ais_time_signatures,
            tempo=ais_tempos,
            time=max_end_time,
            bar=max(num_bars, 100),
        )
        ais_project_body = AISProjectBody(tracks=self.generate_tracks(project.track_list))
        return ais_project_head, ais_project_body

    def generate_time_signatures(
        self, time_signatures: list[TimeSignature]
    ) -> list[AISTimeSignature]:
        return [
            AISTimeSignature(
                beat_zi=time_signature.numerator,
                beat_mu=time_signature.denominator,
                start_bar=time_signature.bar_index,
            )
            for time_signature in time_signatures
        ]

    def generate_tempos(
        self, tempos: list[SongTempo], time_signatures: list[TimeSignature]
    ) -> list[AISTempo]:
        ais_tempos = []
        prev_bar_index = 1
        cur_tick = 0
        tick_indexes = []
        for i, time_signature in enumerate(time_signatures):
            if time_signature.bar_index > prev_bar_index and i:
                cur_tick += time_signature[i - 1].bar_length() * (
                    time_signature.bar_index - prev_bar_index
                )
            tick_indexes.append(cur_tick)
            if time_signature.bar_index > prev_bar_index:
                prev_bar_index = time_signature.bar_index
        for tempo in tempos:
            ts_index = min(
                bisect.bisect_left(tick_indexes, tempo.position),
                len(tick_indexes) - 1,
            )
            start_bar = max(
                (
                    time_signatures[ts_index].bar_index
                    + (tempo.position - tick_indexes[ts_index] - self.first_bar_length)
                    // time_signatures[ts_index].bar_length()
                ),
                0,
            )
            start_beat_in_bar = (
                (tempo.position - tick_indexes[ts_index] - self.first_bar_length)
                % time_signatures[ts_index].bar_length()
            ) // (time_signatures[ts_index].bar_length() / time_signatures[ts_index].numerator)
            ais_tempo = AISTempo(
                tempo_float=tempo.bpm,
                start_128=round(tempo.position / 15),
                start_bar=start_bar,
                start_beat_in_bar=start_beat_in_bar,
            )
            ais_tempos.append(ais_tempo)
        return ais_tempos

    def generate_tracks(self, tracks: list[Track]) -> list[AISSingVoiceTrack]:
        ais_tracks: list[AISSingVoiceTrack] = []
        for track in tracks:
            if isinstance(track, SingingTrack):
                if note_list := self.generate_notes(track):
                    ais_track = AISSingVoiceTrack(
                        idx=len(ais_tracks),
                        name=track.title,
                        mute=track.mute,
                        solo=track.solo,
                        singer_namecn=track.ai_singer_name,
                        items=[
                            AISSingVoicePattern(
                                uid=len(tracks) + len(ais_tracks),
                                start=0,
                                length=max(note.start + note.length for note in note_list),
                                notes=note_list,
                            )
                        ],
                    )
                    ais_tracks.append(ais_track)
            elif isinstance(track, InstrumentalTrack) and (
                track_info := audio_track_info(track.audio_file_path, only_wav=True)
            ):
                offset_secs = track_info.duration / 1000
                end_tick = self.synchronizer.get_actual_ticks_from_secs_offset(
                    track.offset, offset_secs
                )
                ais_track = AISAudioTrack(
                    idx=len(ais_tracks),
                    name=track.title,
                    mute=track.mute,
                    solo=track.solo,
                    items=[
                        AISAudioPattern(
                            start=track.offset // 15,
                            length=(end_tick - track.offset) // 15,
                            path_audio=track.audio_file_path,
                            path_wave=track.audio_file_path,
                            len_sec=int(offset_secs),
                            n_channel=track_info.channel_s,
                        )
                    ],
                )
                ais_tracks.append(ais_track)
        return ais_tracks

    def generate_notes(self, track: SingingTrack) -> list[AISNote]:
        ais_notes = []
        for note in track.note_list:
            ais_note = AISNote(
                midi_no=note.key_number - 12,
                start=round(note.start_pos / 15),
                length=round(note.length / 15),
                lyric=note.lyric,
                pinyin=note.pronunciation
                or (
                    " ".join(get_pinyin_series(note.lyric))
                    if CHINESE_RE.fullmatch(note.lyric) is not None
                    else (note.lyric or DEFAULT_PHONEME)
                ),
                triple=False,
                pit="0x500",
            )
            if pitch_points := self.generate_pitch(track.edited_params.pitch, note):
                ais_note.pit = pitch_points
            ais_notes.append(ais_note)
        return ais_notes

    def generate_pitch(self, pitch_param_curve: ParamCurve, note: Note) -> list[float]:
        tick_step = note.length / 500.0
        sample_time_list = [
            note.start_pos + self.first_bar_length + int(tick_step * i) for i in range(500)
        ]
        pitch_param_in_note = [
            p
            for p in pitch_param_curve.points.root
            if note.start_pos + self.first_bar_length <= p.x < note.end_pos + self.first_bar_length
        ]

        pitch_param_time_in_note = dict(pitch_param_in_note)

        ais_pitch_param: list[Union[int, float]] = []
        for sample_time in sample_time_list:
            if (pitch := pitch_param_time_in_note.get(sample_time)) is None:
                distance = -1
                value = 0.0

                for point in pitch_param_in_note:
                    if distance > abs(point.x - sample_time) or distance == -1:
                        distance = abs(point.x - sample_time)
                        value = 0 if point.y == -100 else (point.y - note.key_number * 100) / 10
                ais_pitch_param.append(value)

            elif pitch == -100:
                ais_pitch_param.append(0)
            else:
                ais_pitch_param.append((pitch - note.key_number * 100) / 10)
        buffer = []
        previous_node = ais_pitch_param[0]
        previous_node_index = 0
        for i in range(len(ais_pitch_param)):
            if ais_pitch_param[i] == previous_node:
                buffer.append(ais_pitch_param[i])
            else:
                for j in range(len(buffer)):
                    ais_pitch_param[previous_node_index + j] = previous_node + j * (
                        ais_pitch_param[i] - buffer[j]
                    ) / len(buffer)
                buffer.clear()

            if ais_pitch_param[i] != previous_node:
                previous_node_index = i
                previous_node = ais_pitch_param[i]

        return ais_pitch_param
