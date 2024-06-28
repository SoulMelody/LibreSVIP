import dataclasses
from collections.abc import Callable
from typing import Optional

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
    VibratoParam,
)
from libresvip.model.point import Point

from .models import opensvip_singers, svip_note_head_tags, svip_reverb_presets
from .msnrbf.xstudio_models import (
    XSAppModel,
    XSInstrumentTrack,
    XSITrack,
    XSLineParam,
    XSNote,
    XSNotePhoneInfo,
    XSSingingTrack,
    XSSongBeat,
    XSSongTempo,
)
from .options import InputOptions


@dataclasses.dataclass
class BinarySvipParser:
    options: InputOptions

    def parse_project(self, version: str, model: XSAppModel) -> Project:
        project = Project()
        project.version = version
        for tempo in model.tempo_list.buf.items:
            project.song_tempo_list.append(self.parse_song_tempo(tempo))
        for beat in model.beat_list.buf.items:
            project.time_signature_list.append(self.parse_time_signature(beat))
        for track in model.track_list.items:
            if (ele := self.parse_track(track)) is not None:
                project.track_list.append(ele)
        return project

    @staticmethod
    def parse_song_tempo(tempo: XSSongTempo) -> SongTempo:
        return SongTempo(position=tempo.pos, bpm=tempo.tempo / 100.0)

    @staticmethod
    def parse_time_signature(beat: XSSongBeat) -> TimeSignature:
        frac = beat.beat_size
        return TimeSignature(
            bar_index=beat.bar_index,
            numerator=frac.x,
            denominator=frac.y,
        )

    def parse_track(self, track: XSITrack) -> Optional[Track]:
        if isinstance(track, XSSingingTrack):
            result_track = SingingTrack()
            result_track.ai_singer_name = opensvip_singers.get_name(track.ai_singer_id)
            result_track.reverb_preset = svip_reverb_presets.inverse.get(track.reverb_preset.value)
            for note in track.note_list.buf.items:
                if (ele := self.parse_note(note)) is not None:
                    result_track.note_list.append(ele)
            result_track.edited_params = self.parse_params(track)
        elif self.options.import_instrumental_track and isinstance(track, XSInstrumentTrack):
            result_track = InstrumentalTrack(
                audio_file_path=track.instrument_file_path,
                offset=track.offset_in_pos,
            )
        else:
            return None
        result_track.title = track.name
        result_track.mute = track.mute
        result_track.solo = track.solo
        result_track.volume = track.volume
        result_track.pan = track.pan
        return result_track

    def parse_params(self, track: XSSingingTrack) -> Params:
        params = Params()
        if self.options.import_pitch and (pitch_line := track.edited_pitch_line) is not None:
            params.pitch = self.parse_param_curve(
                pitch_line, op=lambda x: x - 1150 if x > 1050 else -100
            )
        if self.options.import_volume and (volume_line := track.edited_volume_line) is not None:
            params.breath = self.parse_param_curve(volume_line)
        if self.options.import_breath and (breath_line := track.edited_breath_line) is not None:
            params.breath = self.parse_param_curve(breath_line)
        if self.options.import_gender and (gender_line := track.edited_gender_line) is not None:
            params.gender = self.parse_param_curve(gender_line)
        if self.options.import_strength and (power_line := track.edited_power_line) is not None:
            params.strength = self.parse_param_curve(power_line)
        return params

    def parse_note(self, note: XSNote) -> Note:
        result_note = Note(
            start_pos=note.start_pos,
            length=note.width_pos,
            key_number=note.key_index - 12,
            head_tag=svip_note_head_tags.inverse.get(note.head_tag.value),
            lyric=note.lyric,
        )
        if pronunciation := note.pronouncing:
            result_note.pronunciation = pronunciation
        if (phone := note.note_phone_info) is not None:
            result_note.edited_phones = self.parse_phones(phone)
        if note.vibrato is not None:
            result_note.vibrato = self.parse_vibrato(note)
        return result_note

    def parse_vibrato(self, note: XSNote) -> VibratoParam:
        kwargs = {}
        if note.vibrato_percent_info is not None:
            kwargs["start_percent"] = note.vibrato_percent_info.start_percent
            kwargs["end_percent"] = note.vibrato_percent_info.end_percent
        elif note.vibrato_percent > 0:
            kwargs["start_percent"] = 1.0 - note.vibrato_percent / 100.0
            kwargs["end_percent"] = 1.0
        if note.vibrato is not None:
            kwargs["is_anti_phase"] = note.vibrato.is_anti_phase
            kwargs["amplitude"] = self.parse_param_curve(note.vibrato.amp_line)
            kwargs["frequency"] = self.parse_param_curve(note.vibrato.freq_line)
        return VibratoParam(**kwargs)

    @staticmethod
    def parse_phones(phone: XSNotePhoneInfo) -> Phones:
        return Phones(
            head_length_in_secs=phone.head_phone_time_in_sec,
            mid_ratio_over_tail=phone.mid_part_over_tail_part_ratio,
        )

    @staticmethod
    def parse_param_curve(
        line: XSLineParam, op: Optional[Callable[[float], float]] = None
    ) -> ParamCurve:
        if op is None:

            def op(x: float) -> float:
                return x

        param_curve = ParamCurve()
        for point in line.nodes:
            param_curve.points.append(Point(x=point.pos, y=int(op(point.value))))
        return param_curve
