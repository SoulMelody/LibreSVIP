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
    VibratoParam,
)

from .models import OpenSvipNoteHeadTags, OpenSvipReverbPresets, opensvip_singers
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


class BinarySvipParser:
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
        return SongTempo(Position=tempo.pos, BPM=tempo.tempo / 100.0)

    @staticmethod
    def parse_time_signature(beat: XSSongBeat) -> TimeSignature:
        frac = beat.beat_size
        return TimeSignature(
            BarIndex=beat.bar_index,
            Numerator=frac.x,
            Denominator=frac.y,
        )

    def parse_track(self, track: XSITrack) -> Track:
        if isinstance(track, XSSingingTrack):
            result_track = SingingTrack()
            result_track.ai_singer_name = opensvip_singers.get_name(
                track.ai_singer_id
            )
            result_track.reverb_preset = OpenSvipReverbPresets.get_name(
                track.reverb_preset.value
            )
            for note in track.note_list.buf.items:
                if (ele := self.parse_note(note)) is not None:
                    result_track.note_list.append(ele)
            result_track.edited_params = self.parse_params(track)
        elif isinstance(track, XSInstrumentTrack):
            result_track = InstrumentalTrack()
            result_track.audio_file_path = track.instrument_file_path
            result_track.offset = track.offset_in_pos
        else:
            return None
        result_track.title = track.name
        result_track.mute = track.mute
        result_track.solo = track.solo
        result_track.volume = track.volume
        result_track.pan = track.pan
        return result_track

    def parse_params(self, track: XSSingingTrack) -> Params:
        kwargs = {}
        if (pitch_line := track.edited_pitch_line) is not None:
            kwargs["Pitch"] = self.parse_param_curve(
                pitch_line, op=lambda x: x - 1150 if x > 1050 else -100
            )
        if (volume_line := track.edited_volume_line) is not None:
            kwargs["Volume"] = self.parse_param_curve(volume_line)
        if (breath_line := track.edited_breath_line) is not None:
            kwargs["Breath"] = self.parse_param_curve(breath_line)
        if (gender_line := track.edited_gender_line) is not None:
            kwargs["Gender"] = self.parse_param_curve(gender_line)
        if (power_line := track.edited_power_line) is not None:
            kwargs["Power"] = self.parse_param_curve(power_line)
        params = Params(**kwargs)
        return params

    def parse_note(self, note: XSNote) -> Note:
        result_note = Note(
            StartPos=note.start_pos,
            Length=note.width_pos,
            KeyNumber=note.key_index - 12,
            HeadTag=OpenSvipNoteHeadTags.get_name(note.head_tag.value),
            Lyric=note.lyric,
        )
        if (pronunciation := note.pronouncing) != "":
            result_note.pronunciation = pronunciation
        phone = note.note_phone_info
        if phone is not None:
            result_note.edited_phones = self.parse_phones(phone)
        vibrato = note.vibrato
        if vibrato is not None:
            result_note.vibrato = self.parse_vibrato(note)
        return result_note

    def parse_vibrato(self, note: XSNote) -> VibratoParam:
        percent = note.vibrato_percent_info
        kwargs = {}
        if percent is not None:
            kwargs["StartPercent"] = percent.start_percent
            kwargs["EndPercent"] = percent.end_percent
        elif note.vibrato_percent > 0:
            kwargs["StartPercent"] = 1.0 - note.vibrato_percent / 100.0
            kwargs["EndPercent"] = 1.0
        vibrato = note.vibrato
        result_vibrato = VibratoParam(
            IsAntiPhase=vibrato.is_anti_phase,
            Amplitude=self.parse_param_curve(vibrato.amp_line),
            Frequency=self.parse_param_curve(vibrato.freq_line),
            **kwargs,
        )
        return result_vibrato

    @staticmethod
    def parse_phones(phone: XSNotePhoneInfo) -> Phones:
        return Phones(
            HeadLengthInSecs=phone.head_phone_time_in_sec,
            MidRatioOverTail=phone.mid_part_over_tail_part_ratio,
        )

    @staticmethod
    def parse_param_curve(line: XSLineParam, op=lambda x: x) -> ParamCurve:
        param_curve = ParamCurve()
        for point in line.nodes:
            param_curve.points.append(Point(x=point.pos, y=op(point.value)))
        return param_curve
