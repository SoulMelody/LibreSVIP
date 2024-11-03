import dataclasses
import sys
from collections.abc import Callable
from typing import TYPE_CHECKING, Optional

from libresvip.core.tick_counter import skip_beat_list
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import (
    InstrumentalTrack,
    Note,
    ParamCurve,
    Params,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
    Track,
)
from libresvip.model.pitch_simulator import PitchSimulator
from libresvip.model.portamento import PortamentoPitch
from libresvip.utils.audio import audio_track_info
from libresvip.utils.music_math import (
    clamp,
    ratio_to_db,
)
from libresvip.utils.search import find_index, find_last_index

from .constants import TICK_RATE
from .interval_utils import ticks_to_position
from .model import (
    SVAudio,
    SVMeter,
    SVMixer,
    SVNote,
    SVParamCurve,
    SVParameters,
    SVPoint,
    SVProject,
    SVTempo,
    SVTrack,
)
from .options import (
    OutputOptions,
    SVProjectVersionCompatibility,
    VibratoOption,
    synthv_language_presets,
)
from .phoneme_utils import default_phone_marks, number_of_phones, sv_g2p

if TYPE_CHECKING:
    from libresvip.model.point import Point


@dataclasses.dataclass
class SynthVGenerator:
    options: OutputOptions
    first_bar_tick: int = dataclasses.field(init=False)
    first_bar_tempo: list[SongTempo] = dataclasses.field(init=False)
    note_buffer: list[Note] = dataclasses.field(init=False)
    synchronizer: TimeSynchronizer = dataclasses.field(init=False)
    pitch_simulator: PitchSimulator = dataclasses.field(init=False)
    no_vibrato_indexes: set[int] = dataclasses.field(init=False)
    lyrics_phonemes: list[str] = dataclasses.field(init=False)

    def generate_project(self, project: Project) -> SVProject:
        sv_project = SVProject()
        if self.options.version_compatibility == SVProjectVersionCompatibility.BELOW_1_9_0:
            sv_project.instant_mode_enabled = False
        else:
            sv_project.version = SVProjectVersionCompatibility.ABOVE_1_9_0.value
        new_meters = skip_beat_list(project.time_signature_list, 1)
        self.first_bar_tick = round(project.time_signature_list[0].bar_length())
        self.first_bar_tempo = [
            tempo for tempo in project.song_tempo_list if tempo.position < self.first_bar_tick
        ]
        self.synchronizer = TimeSynchronizer(project.song_tempo_list, self.first_bar_tick)
        for tempo in self.synchronizer.tempo_list:
            sv_project.time_sig.tempo.append(self.generate_tempo(tempo))
        if any(
            (beat.denominator < 2 or beat.denominator > 16) for beat in project.time_signature_list
        ):
            sv_project.time_sig.meter.append(SVMeter(index=0, numerator=4, denominator=4))
        else:
            for meter in new_meters:
                sv_project.time_sig.meter.append(self.generate_meter(meter))
        for track_id, track in enumerate(project.track_list):
            if (sv_track := self.generate_track(track)) is not None:
                sv_track.disp_order = track_id
                sv_project.tracks.append(sv_track)
        return sv_project

    @staticmethod
    def generate_tempo(tempo: SongTempo) -> SVTempo:
        return SVTempo(position=ticks_to_position(tempo.position), bpm=tempo.bpm)

    @staticmethod
    def generate_meter(signature: TimeSignature) -> SVMeter:
        return SVMeter(
            index=signature.bar_index,
            numerator=signature.numerator,
            denominator=signature.denominator,
        )

    def generate_track(self, track: Track) -> Optional[SVTrack]:
        sv_track = SVTrack(
            name=track.title,
            mixer=SVMixer(
                gain_decibel=self.generate_volume(track.volume),
                pan=track.pan,
                mute=track.mute,
                solo=track.solo,
            ),
        )
        if isinstance(track, SingingTrack):
            sv_track.main_ref.is_instrumental = False
            sv_track.disp_color = "ff7db235"
            language_preset = synthv_language_presets[self.options.language_override.value]
            sv_track.main_ref.database.language_override = language_preset.language
            sv_track.main_ref.database.phoneset_override = language_preset.phoneset
            if track.ai_singer_name:
                sv_track.main_ref.database.name = track.ai_singer_name
            self.note_buffer = track.note_list
            self.pitch_simulator = PitchSimulator(
                synchronizer=self.synchronizer,
                note_list=track.note_list,
                portamento=PortamentoPitch.sigmoid_portamento(),
            )
            sv_track.main_group.parameters = self.generate_params(track.edited_params)

            self.lyrics_phonemes = sv_g2p(
                (SVNote.normalize_phoneme(note) for note in track.note_list),
                [language_preset.language] * len(track.note_list),
            )

            sv_track.main_group.notes = self.generate_notes_with_phones(track.note_list)

            if self.options.vibrato == VibratoOption.NONE:
                for note in sv_track.main_group.notes:
                    note.attributes.vibrato_depth = 0
            elif self.options.vibrato == VibratoOption.HYBRID:
                for index in self.no_vibrato_indexes:
                    sv_track.main_group.notes[index].attributes.vibrato_depth = 0
        elif isinstance(track, InstrumentalTrack):
            sv_track.main_ref.is_instrumental = True
            sv_track.disp_color = "ff4794cb"
            sv_track.main_ref.audio = SVAudio(filename=track.audio_file_path, duration=0)
            sv_track.main_ref.blick_offset = self.generate_audio_offset(track.offset)
            if (track_info := audio_track_info(track.audio_file_path)) is not None:
                sv_track.main_ref.audio.duration = track_info.duration / 1000
        else:
            return None
        return sv_track

    def generate_audio_offset(self, offset: int) -> int:
        if offset >= 0:
            return ticks_to_position(offset)
        current_pos = self.first_bar_tick
        actual_pos = self.first_bar_tick + offset
        res = 0.0
        i = len(self.first_bar_tempo) - 1
        for i in range(len(self.first_bar_tempo) - 1, -1, -1):
            if actual_pos > self.first_bar_tempo[i].position:
                break
            res -= (
                (current_pos - self.first_bar_tempo[i].position) * 120 / self.first_bar_tempo[i].bpm
            )
            current_pos = self.first_bar_tempo[i].position
        if i >= 0:
            res -= (current_pos - actual_pos) * 120 / self.first_bar_tempo[i].bpm
        else:
            res += actual_pos * 120 / self.first_bar_tempo[0].bpm
        return round(res * TICK_RATE)

    @staticmethod
    def generate_volume(volume: float) -> float:
        return max(ratio_to_db(max(volume, 0.06)), -24.0)

    def generate_params(self, parameters: Params) -> SVParameters:
        return SVParameters(
            pitch_delta=self.generate_pitch_curve(
                parameters.pitch.reduce_sample_rate(self.options.down_sample, -100)
            ),
            loudness=self.generate_param_curve(
                parameters.volume.reduce_sample_rate(self.options.down_sample),
                0,
                0.0,
                lambda val: (
                    val / 1000.0 * 12.0
                    if val >= 0
                    else max(
                        ratio_to_db(val / 1000.0 + 1.0 if val > -997 else 0.0039),
                        -48.0,
                    )
                ),
            ),
            tension=self.generate_param_curve(
                parameters.strength.reduce_sample_rate(self.options.down_sample),
                0,
                0.0,
                (1000.0).__rtruediv__,
            ),
            breathiness=self.generate_param_curve(
                parameters.breath.reduce_sample_rate(self.options.down_sample),
                0,
                0.0,
                (1000.0).__rtruediv__,
            ),
        )

    def generate_pitch_curve(self, curve: ParamCurve) -> SVParamCurve:
        sv_curve = SVParamCurve()
        if self.options.vibrato == VibratoOption.HYBRID:
            self.no_vibrato_indexes = set()
        if not len(self.note_buffer):
            return sv_curve
        point_list = sv_curve.points
        buffer: list[Point] = []
        min_interval = 1
        last_point = None
        for point in curve.points.root:
            if point.x >= self.first_bar_tick:
                point = point._replace(x=point.x - self.first_bar_tick)
                if point.y == -100:
                    if not len(buffer):
                        continue
                    if last_point is None or last_point.x + min_interval < buffer[0].x:
                        if last_point is not None and last_point.x + 2 * min_interval < buffer[0].x:
                            point_list.append(
                                SVPoint(
                                    offset=ticks_to_position(last_point.x + min_interval),
                                    value=0,
                                )
                            )
                        point_list.append(
                            SVPoint(
                                offset=ticks_to_position(buffer[0].x - min_interval),
                                value=0,
                            )
                        )
                    for tmp_point in buffer:
                        point_list.append(
                            SVPoint(
                                offset=ticks_to_position(tmp_point.x),
                                value=self.generate_pitch_diff(tmp_point.x, tmp_point.y),
                            )
                        )
                    last_point = buffer[-1]
                    buffer.clear()
                else:
                    buffer.append(point)
        if last_point is not None:
            point_list.append(
                SVPoint(
                    offset=ticks_to_position(last_point.x + min_interval),
                    value=0,
                )
            )
        return sv_curve

    def generate_note(self, note: Note) -> SVNote:
        onset = ticks_to_position(note.start_pos)
        return SVNote(
            instant_mode=False
            if self.options.version_compatibility == SVProjectVersionCompatibility.ABOVE_1_9_0
            else None,
            onset=onset,
            pitch=note.key_number,
            lyrics=note.lyric or note.pronunciation or "",
            duration=ticks_to_position(note.end_pos) - onset,
        )

    def generate_pitch_diff(self, pos: int, pitch: int) -> float:
        target_note_index = find_last_index(self.note_buffer, lambda x: x.start_pos <= pos)
        target_note = self.note_buffer[target_note_index] if target_note_index >= 0 else None
        if (
            simulated_pitch := self.pitch_simulator.pitch_at_secs(
                self.synchronizer.get_actual_secs_from_ticks(pos)
            )
        ) is not None:
            pitch_diff = pitch - simulated_pitch
        else:
            pitch_diff = 0.0
        if target_note is None:
            return pitch_diff
        if (
            self.options.vibrato == VibratoOption.HYBRID
            and self.synchronizer.get_duration_secs_from_ticks(target_note.start_pos, pos) > 0.25
            and pos < target_note.end_pos
        ):
            self.no_vibrato_indexes.add(target_note_index)
        return pitch_diff

    def generate_param_curve(
        self,
        curve: ParamCurve,
        termination: int,
        default_value: float,
        mapping_func: Callable[[int], float],
    ) -> SVParamCurve:
        sv_curve = SVParamCurve()
        if not len(curve.points):
            return sv_curve
        if self.options.down_sample > 15:
            sv_curve.mode = "cubic"
        skipped = 0
        point_list = sv_curve.points
        if curve.points[0].x == -192000:
            if len(curve.points) == 2 and curve.points[1].x == sys.maxsize // 2:
                if curve.points[0].y != termination:
                    point_list.append(SVPoint(offset=0, value=mapping_func(curve.points[0].y)))
                return sv_curve
            skipped = 1
            valid_index = find_index(curve.points.root, lambda x: x.x >= self.first_bar_tick)
            if (
                valid_index != -1
                and len(curve.points) > valid_index + 1
                and (
                    curve.points[valid_index].y != termination
                    or curve.points[valid_index + 1].y != termination
                    or curve.points[valid_index + 1].x >= sys.maxsize // 2
                )
            ):
                skipped = valid_index + 1
                x0 = curve.points[valid_index].x
                y0 = curve.points[valid_index].y
                point_list.append(
                    SVPoint(
                        offset=ticks_to_position(x0 - self.first_bar_tick),
                        value=mapping_func(y0),
                    )
                )
        buffer: list[Point] = []
        min_interval = 1
        last_point = None
        for point in curve.points.root[skipped:]:
            if self.first_bar_tick <= point.x < sys.maxsize // 2:
                point = point._replace(x=point.x - self.first_bar_tick)
                if point.y == termination:
                    if not len(buffer):
                        continue
                    if last_point is None or last_point.x + min_interval < buffer[0].x:
                        if last_point is not None and last_point.x + 2 * min_interval < buffer[0].x:
                            point_list.append(
                                SVPoint(
                                    offset=ticks_to_position(last_point.x + min_interval),
                                    value=default_value,
                                )
                            )
                        point_list.append(
                            SVPoint(
                                offset=ticks_to_position(buffer[0].x - min_interval),
                                value=default_value,
                            )
                        )
                    for tmp_point in buffer:
                        point_list.append(
                            SVPoint(
                                offset=ticks_to_position(tmp_point.x),
                                value=mapping_func(tmp_point.y),
                            )
                        )
                    last_point = buffer[-1]
                    buffer.clear()
                else:
                    buffer.append(point)

        if not len(buffer):
            if last_point is not None:
                point_list.append(
                    SVPoint(
                        offset=ticks_to_position(last_point.x + min_interval),
                        value=default_value,
                    )
                )
            return sv_curve
        if last_point is None or last_point.x + min_interval < buffer[0].x:
            if last_point is not None and last_point.x + 2 * min_interval < buffer[0].x:
                point_list.append(
                    SVPoint(
                        offset=ticks_to_position(last_point.x + min_interval),
                        value=default_value,
                    )
                )
            point_list.append(
                SVPoint(
                    offset=ticks_to_position(buffer[0].x - min_interval),
                    value=default_value,
                )
            )
        for tmp_point in buffer:
            point_list.append(
                SVPoint(
                    offset=ticks_to_position(tmp_point.x),
                    value=mapping_func(tmp_point.y),
                )
            )
        last_point = buffer[-1]
        buffer.clear()
        if last_point.y == termination:
            point_list.append(
                SVPoint(
                    offset=ticks_to_position(last_point.x + min_interval),
                    value=default_value,
                )
            )
        return sv_curve

    def generate_notes_with_phones(self, notes: list[Note]) -> list[SVNote]:
        sv_note_list: list[SVNote] = []
        if not len(notes):
            return sv_note_list
        current_note = notes[0]
        current_sv_note = self.generate_note(current_note)
        current_phone_marks = default_phone_marks(
            self.lyrics_phonemes[0], self.options.language_override.value
        )
        if (
            current_phone_marks[0] > 0
            and notes[0].edited_phones is not None
            and notes[0].edited_phones.head_length_in_secs > 0
        ):
            ratio = notes[0].edited_phones.head_length_in_secs / current_phone_marks[0]
            current_sv_note.attributes.set_phone_duration(0, clamp(ratio, 0.2, 1.8))
        for next_note, cur_phoneme, next_phoneme in zip(
            notes[1:], self.lyrics_phonemes[:-1], self.lyrics_phonemes[1:]
        ):
            next_sv_note = self.generate_note(next_note)
            next_phone_marks = default_phone_marks(
                next_phoneme, self.options.language_override.value
            )

            current_main_part_edited = (
                current_phone_marks[1] > 0
                and current_note.edited_phones is not None
                and current_note.edited_phones.mid_ratio_over_tail > 0
            )
            next_head_part_edited = (
                next_phone_marks[0] > 0
                and next_note.edited_phones is not None
                and next_note.edited_phones.head_length_in_secs > 0
            )

            index = 1 if current_phone_marks[0] > 0 else 0
            if (
                current_main_part_edited
                and next_head_part_edited
                and (current_note.edited_phones is not None)
                and (next_note.edited_phones is not None)
            ):
                current_main_ratio = (
                    current_note.edited_phones.mid_ratio_over_tail / current_phone_marks[1]
                )
                next_head_ratio = next_note.edited_phones.head_length_in_secs / next_phone_marks[0]
                x = 2 * current_main_ratio / (1 + current_main_ratio)
                y = 2 / (1 + current_main_ratio)
                z = next_head_ratio
                if (
                    self.synchronizer.get_duration_secs_from_ticks(
                        current_note.end_pos, next_note.start_pos
                    )
                    < next_phone_marks[0]
                ):
                    final_ratio = 2 / (1 + next_head_ratio)
                    x *= final_ratio
                    y *= final_ratio
                    z *= final_ratio
                current_sv_note.attributes.set_phone_duration(index, clamp(x, 0.2, 1.8))
                current_sv_note.attributes.set_phone_duration(index + 1, clamp(y, 0.2, 1.8))
                next_sv_note.attributes.set_phone_duration(0, clamp(z, 0.2, 1.8))
            elif current_main_part_edited and current_note.edited_phones is not None:
                ratio = current_note.edited_phones.mid_ratio_over_tail / current_phone_marks[1]
                x = 2 * ratio / (1 + ratio)
                y = 2 / (1 + ratio)
                current_sv_note.attributes.set_phone_duration(index, clamp(x, 0.2, 1.8))
                current_sv_note.attributes.set_phone_duration(index + 1, clamp(y, 0.2, 1.8))
            elif next_head_part_edited and next_note.edited_phones is not None:
                ratio = next_note.edited_phones.head_length_in_secs / next_phone_marks[0]
                if (
                    self.synchronizer.get_duration_secs_from_ticks(
                        current_note.end_pos, next_note.start_pos
                    )
                    < next_phone_marks[0]
                ):
                    ratio_z = 2 * ratio / (1 + ratio)
                    ratio_xy = 2 / (1 + ratio)
                    ratio_z = clamp(ratio_z, 0.2, 1.8)
                    ratio_xy = clamp(ratio_xy, 0.2, 1.8)
                    current_sv_note.attributes.set_phone_duration(index, ratio_xy)
                    if current_phone_marks[1] > 0:
                        current_sv_note.attributes.set_phone_duration(index + 1, ratio_xy)
                    ratio = ratio_z
                next_sv_note.attributes.set_phone_duration(0, ratio)
            if current_sv_note.attributes.dur is not None:
                expected_length = number_of_phones(
                    cur_phoneme, self.options.language_override.value
                )
                if len(current_sv_note.attributes.dur) < expected_length:
                    current_sv_note.attributes.set_phone_duration(expected_length - 1, 1.0)

            sv_note_list.append(current_sv_note)

            current_note = next_note
            current_sv_note = next_sv_note
            current_phone_marks = next_phone_marks
        if (
            current_phone_marks[1] > 0
            and current_note.edited_phones is not None
            and current_note.edited_phones.mid_ratio_over_tail > 0
            and notes[-1].edited_phones is not None
        ):
            ratio = notes[-1].edited_phones.mid_ratio_over_tail / current_phone_marks[1]
            x = 2 * ratio / (1 + ratio)
            y = 2 / (1 + ratio)
            index = 1 if current_phone_marks[0] > 0 else 0
            current_sv_note.attributes.set_phone_duration(index, clamp(x, 0.2, 1.8))
            current_sv_note.attributes.set_phone_duration(index + 1, clamp(y, 0.2, 1.8))
        if current_sv_note.attributes.dur is not None:
            expected_length = number_of_phones(
                self.lyrics_phonemes[-1], self.options.language_override.value
            )
            if len(current_sv_note.attributes.dur) < expected_length:
                current_sv_note.attributes.set_phone_duration(expected_length - 1, 1.0)
        sv_note_list.append(current_sv_note)
        return sv_note_list
