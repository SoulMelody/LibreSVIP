import dataclasses
from typing import Optional

from libresvip.core.constants import DEFAULT_ENGLISH_LYRIC
from libresvip.core.tick_counter import skip_beat_list, skip_tempo_list
from libresvip.model.base import (
    InstrumentalTrack,
    Note,
    ParamCurve,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
)

from .constants import BPM_RATE
from .model import (
    Vsq3ParameterNames,
    Vsq4ParameterNames,
    Vsqx,
    VsqxMasterTrack,
    VsqxMCtrl,
    VsqxNote,
    VsqxParameterNames,
    VsqxTempo,
    VsqxTimeSig,
    VsqxVsTrack,
    VsqxVsUnit,
    VsqxWavPart,
)
from .options import InputOptions
from .vocaloid_pitch import (
    ControllerEvent,
    VocaloidPartPitchData,
    pitch_from_vocaloid_parts,
)


@dataclasses.dataclass
class VsqxParser:
    options: InputOptions
    param_names: VsqxParameterNames = dataclasses.field(init=False)

    def parse_project(self, vsqx_project: Vsqx) -> Project:
        if vsqx_project.Meta.name == "vsq3":
            self.param_names = Vsq3ParameterNames
        elif vsqx_project.Meta.name == "vsq4":
            self.param_names = Vsq4ParameterNames
        master_track: VsqxMasterTrack = vsqx_project.master_track
        measure_prefix = master_track.pre_measure
        tick_prefix, time_signatures = self.parse_time_signatures(
            master_track.time_sig, measure_prefix
        )
        tempos = self.parse_tempos(master_track.tempo, tick_prefix)
        singing_tracks = self.parse_singing_tracks(vsqx_project.vs_track, vsqx_project.mixer.vs_unit, tick_prefix)
        wav_parts = []
        wav_units = []
        if vsqx_project.mono_track is not None:
            wav_parts += vsqx_project.mono_track.wav_part
            wav_units += [vsqx_project.mixer.mono_unit] * len(
                vsqx_project.mono_track.wav_part
            )
        if vsqx_project.stereo_track is not None:
            wav_parts += vsqx_project.stereo_track.wav_part
            wav_units += [vsqx_project.mixer.stereo_unit] * len(
                vsqx_project.stereo_track.wav_part
            )
        instrumental_tracks = self.parse_instrumental_tracks(wav_parts, wav_units, tick_prefix)
        return Project(
            song_tempo_list=tempos,
            time_signature_list=time_signatures,
            track_list=singing_tracks + instrumental_tracks,
        )

    def parse_time_signatures(
        self, time_signatures: list[VsqxTimeSig], measure_prefix: int
    ) -> tuple[int, list[TimeSignature]]:
        time_signature_list = [
            TimeSignature(
                numerator=time_sig.nume,
                denominator=time_sig.denomi,
                bar_index=time_sig.pos_mes,
            )
            for time_sig in time_signatures
        ]
        tick_prefix = 0
        measure = 0
        for time_sig in time_signature_list:
            measure_diff = time_sig.bar_index - measure
            tick_prefix += measure_diff * time_sig.bar_length()
            measure += time_sig.bar_index
        measure_diff = measure_prefix - measure
        tick_prefix += measure_diff * time_signature_list[-1].bar_length()
        return int(tick_prefix), skip_beat_list(time_signature_list, measure_prefix)

    def parse_tempos(
        self, tempos: list[VsqxTempo], tick_prefix: int
    ) -> list[SongTempo]:
        tempo_list = [
            SongTempo(
                position=tempo.pos_tick,
                bpm=tempo.bpm / BPM_RATE,
            )
            for tempo in tempos
        ]
        return skip_tempo_list(tempo_list, tick_prefix)

    def parse_singing_tracks(
        self,
        vs_tracks: list[VsqxVsTrack],
        vs_units: list[VsqxVsUnit],
        tick_prefix: int,
    ) -> list[SingingTrack]:
        singing_tracks = []
        for vs_track, vs_unit in zip(vs_tracks, vs_units):
            singing_track = SingingTrack(title=vs_track.track_name, mute=vs_unit.mute, solo=vs_unit.solo)
            for musical_part in vs_track.musical_part:
                tick_offset = musical_part.pos_tick - tick_prefix
                note_list = self.parse_notes(musical_part.note, tick_prefix)
                singing_track.note_list.extend(note_list)
                if pitch := self.parse_pitch(
                    musical_part.m_ctrl, note_list, tick_offset
                ):
                    singing_track.edited_params.pitch.points.extend(pitch.points)
            singing_tracks.append(singing_track)
        return singing_tracks

    def parse_notes(self, notes: list[VsqxNote], tick_offset: int) -> list[Note]:
        return [
            Note(
                start_pos=note.pos_tick + tick_offset,
                length=note.dur_tick,
                lyric=note.lyric or DEFAULT_ENGLISH_LYRIC,
                pronunciation=note.phnms.value if note.phnms is not None else None,
                key_number=note.note_num,
            )
            for note in notes
        ]

    def parse_pitch(
        self, music_controls: list[VsqxMCtrl], note_list: list[Note], tick_offset: int
    ) -> Optional[ParamCurve]:
        pitch_data = VocaloidPartPitchData(
            start_pos=tick_offset,
            pit=[
                ControllerEvent(
                    pos=music_control.pos_tick,
                    value=music_control.attr.value,
                )
                for music_control in music_controls
                if music_control.attr.id == self.param_names.PIT
            ],
            pbs=[
                ControllerEvent(
                    pos=music_control.pos_tick,
                    value=music_control.attr.value,
                )
                for music_control in music_controls
                if music_control.attr.id == self.param_names.PBS
            ],
        )
        return pitch_from_vocaloid_parts([pitch_data], note_list)

    def parse_instrumental_tracks(
        self,
        wav_parts: list[VsqxWavPart],
        wav_units: list[VsqxVsUnit],
        tick_prefix: int,
    ) -> list[InstrumentalTrack]:
        return [
            InstrumentalTrack(
                title=wav_part.part_name,
                audio_file_path=wav_part.file_path,
                offset=wav_part.pos_tick - tick_prefix,
                mute=wav_unit.mute,
                solo=wav_unit.solo,
            )
            for wav_part, wav_unit in zip(wav_parts, wav_units)
        ]
