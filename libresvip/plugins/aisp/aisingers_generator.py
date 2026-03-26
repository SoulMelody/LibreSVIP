import bisect
import dataclasses

from libresvip.core.constants import DEFAULT_PHONEME
from libresvip.core.lyric_phoneme.chinese import CHINESE_RE, get_pinyin_series
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
from libresvip.model.pitch_simulator import PitchSimulator
from libresvip.model.portamento import PortamentoPitch
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
        ais_project_body = AISProjectBody(
            tracks=self.generate_tracks(project.track_list, project.time_signature_list)
        )
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
        prev_bar_length = 1920.0
        prev_bar_index = 1
        cur_tick = 0.0
        tick_indexes = []
        for i, time_signature in enumerate(time_signatures):
            if time_signature.bar_index > prev_bar_index and i:
                cur_tick += prev_bar_length * (time_signature.bar_index - prev_bar_index)
            tick_indexes.append(int(cur_tick))
            if time_signature.bar_index > prev_bar_index:
                prev_bar_index = time_signature.bar_index
                prev_bar_length = time_signature.bar_length()
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

    def generate_tracks(
        self, tracks: list[Track], time_signatures: list[TimeSignature]
    ) -> list[AISSingVoiceTrack]:
        ais_tracks: list[AISSingVoiceTrack] = []
        for track in tracks:
            if isinstance(track, SingingTrack):
                if note_list := self.generate_notes(track, time_signatures):
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
                                length=max(note.start + note.length for note in note_list)
                                + self.first_bar_length,
                                notes=note_list,
                            )
                        ],
                    )
                    ais_tracks.append(ais_track)
            elif isinstance(track, InstrumentalTrack) and (
                track_info := audio_track_info(track.audio_file_path, only_wav=True)
            ):
                offset_secs = track_info.duration
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
                            n_channel=track_info.channels,
                        )
                    ],
                )
                ais_tracks.append(ais_track)
        return ais_tracks

    def generate_notes(
        self, singing_track: SingingTrack, time_signatures: list[TimeSignature]
    ) -> list[AISNote]:
        ais_notes = []
        pitch_simulator = None
        for note in singing_track.note_list:
            note_start = int(note.start_pos / 15)
            ais_note = AISNote(
                midi_no=note.key_number - 12,
                start=note_start,
                length=int(note.end_pos / 15) - note_start,
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
            if singing_track.edited_params.pitch:
                if pitch_simulator is None:
                    pitch_simulator = PitchSimulator(
                        synchronizer=self.synchronizer,
                        portamento=PortamentoPitch.no_portamento(),
                        note_list=singing_track.note_list,
                        time_signature_list=time_signatures,
                    )
                    pitch_simulator.merge_pitch_curve(
                        singing_track.edited_params.pitch, self.first_bar_length
                    )
                pitch_points = self.generate_pitch(pitch_simulator, note)
                ais_note.pit = pitch_points
            ais_notes.append(ais_note)
        return ais_notes

    def generate_pitch(self, pitch_simulator: PitchSimulator, note: Note) -> list[float]:
        tick_step = note.length / 500.0
        ais_pitch_param = []
        for i in range(500):
            pitch_value = pitch_simulator.pitch_at_ticks(note.start_pos + int(tick_step * i))
            if pitch_value is None:
                pitch_value = note.key_number * 100
            value = (pitch_value - note.key_number * 100) / 10
            ais_pitch_param.append(value)

        return ais_pitch_param
