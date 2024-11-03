import dataclasses
import functools
import math
import pathlib
from typing import Optional

import more_itertools
import portion

from libresvip.core.constants import DEFAULT_ENGLISH_LYRIC
from libresvip.core.tick_counter import skip_beat_list, skip_tempo_list
from libresvip.core.time_interval import PiecewiseIntervalDict
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import (
    InstrumentalTrack,
    Note,
    ParamCurve,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
)
from libresvip.model.point import Point

from .constants import BPM_RATE
from .model import (
    Vsq3ParameterNames,
    Vsq4ParameterNames,
    Vsqx,
    VsqxMasterTrack,
    VsqxMusicalPart,
    VsqxNote,
    VsqxParameterNames,
    VsqxTempoList,
    VsqxTimeSigList,
    VsqxVsTrackList,
    VsqxVsUnitList,
    VsqxVVoice,
    VsqxWavPartList,
    VsqxWavUnitList,
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
    src_path: pathlib.Path
    param_names: type[VsqxParameterNames] = dataclasses.field(init=False)
    first_bar_length: int = dataclasses.field(init=False)
    synchronizer: TimeSynchronizer = dataclasses.field(init=False)
    pc2voice: dict[int, VsqxVVoice] = dataclasses.field(default_factory=dict)

    def parse_project(self, vsqx_project: Vsqx) -> Project:
        if vsqx_project.Meta.name == "vsq3":
            self.param_names = Vsq3ParameterNames
        elif vsqx_project.Meta.name == "vsq4":
            self.param_names = Vsq4ParameterNames
        master_track: VsqxMasterTrack = vsqx_project.master_track
        tick_prefix, time_signatures = self.parse_time_signatures(
            master_track.time_sig, master_track.pre_measure
        )
        tempos = self.parse_tempos(master_track.tempo, tick_prefix)
        self.synchronizer = TimeSynchronizer(tempos)
        for v_voice in vsqx_project.v_voice_table.v_voice:
            if v_voice.v_pc is not None:
                self.pc2voice[v_voice.v_pc] = v_voice
        singing_tracks = self.parse_singing_tracks(
            vsqx_project.vs_track, vsqx_project.mixer.vs_unit, tick_prefix
        )
        wav_parts: VsqxWavPartList = []
        wav_units: VsqxWavUnitList = []
        if vsqx_project.mono_track is not None:
            wav_parts += vsqx_project.mono_track.wav_part
            wav_units += [vsqx_project.mixer.mono_unit] * len(vsqx_project.mono_track.wav_part)
        if vsqx_project.stereo_track is not None:
            wav_parts += vsqx_project.stereo_track.wav_part
            wav_units += [vsqx_project.mixer.stereo_unit] * len(vsqx_project.stereo_track.wav_part)
        instrumental_tracks = self.parse_instrumental_tracks(wav_parts, wav_units, tick_prefix)
        return Project(
            song_tempo_list=tempos,
            time_signature_list=time_signatures,
            track_list=singing_tracks + instrumental_tracks,
        )

    def parse_time_signatures(
        self, time_signatures: VsqxTimeSigList, measure_prefix: int
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
            tick_prefix += measure_diff * round(time_sig.bar_length())
            measure += time_sig.bar_index
        measure_diff = measure_prefix - measure
        tick_prefix += measure_diff * round(time_signature_list[-1].bar_length())
        self.first_bar_length = round(time_signature_list[0].bar_length())
        return int(tick_prefix), skip_beat_list(time_signature_list, measure_prefix)

    def parse_tempos(self, tempos: VsqxTempoList, tick_prefix: int) -> list[SongTempo]:
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
        vs_tracks: VsqxVsTrackList,
        vs_units: VsqxVsUnitList,
        tick_prefix: int,
    ) -> list[SingingTrack]:
        singing_tracks = []
        for vs_track, vs_unit in zip(vs_tracks, vs_units):
            singing_track = SingingTrack(
                title=vs_track.track_name, mute=vs_unit.mute, solo=vs_unit.solo
            )
            for musical_part in vs_track.musical_part:
                (
                    note_list,
                    vibrato_rate_interval_dict,
                    vibrato_depth_interval_dict,
                ) = self.parse_notes(musical_part.note, musical_part.pos_tick - tick_prefix)
                singing_track.note_list.extend(note_list)
                if (
                    not singing_track.ai_singer_name
                    and musical_part.singer
                    and (v_voice := self.pc2voice.get(musical_part.singer[0].v_pc))
                    and v_voice.v_voice_name is not None
                ):
                    singing_track.ai_singer_name = v_voice.v_voice_name
                if self.options.import_pitch and (
                    pitch := self.parse_pitch(
                        musical_part,
                        note_list,
                        vibrato_rate_interval_dict,
                        vibrato_depth_interval_dict,
                        tick_prefix,
                    )
                ):
                    singing_track.edited_params.pitch.points.extend(pitch.points)
            if len(singing_track.edited_params.pitch.points.root):
                singing_track.edited_params.pitch.points.root.insert(0, Point.start_point())
                singing_track.edited_params.pitch.points.root.append(Point.end_point())
            singing_tracks.append(singing_track)
        return singing_tracks

    @staticmethod
    def vibrato_curve(value: float, shift: float, omega: float, phase: float) -> float:
        return math.cos(omega * (value - shift) + phase)

    def parse_notes(
        self, vsqx_notes: list[VsqxNote], tick_offset: int
    ) -> tuple[list[Note], PiecewiseIntervalDict, PiecewiseIntervalDict]:
        prev_vsqx_note = None
        note_list: list[Note] = []
        vibrato_depth_interval_dict = PiecewiseIntervalDict()
        vibrato_rate_interval_dict = PiecewiseIntervalDict()
        for vsqx_note in vsqx_notes:
            if prev_vsqx_note and vsqx_note.lyric.startswith("EVEC("):
                note_list[-1].length += vsqx_note.dur_tick
                continue
            elif vsqx_note.phnms is None or vsqx_note.phnms.value not in [
                "Asp",
                "Sil",
                "?",
            ]:
                note = Note(
                    start_pos=vsqx_note.pos_tick + tick_offset,
                    length=vsqx_note.dur_tick,
                    lyric=(vsqx_note.lyric or DEFAULT_ENGLISH_LYRIC).lower(),
                    pronunciation=vsqx_note.phnms.value
                    if (vsqx_note.phnms is not None and vsqx_note.phnms.lock == 1)
                    else None,
                    key_number=vsqx_note.note_num,
                )
                if vsqx_note.note_style.seq_attr:
                    start_secs = self.synchronizer.get_actual_secs_from_ticks(note.start_pos)
                    duration_secs = self.synchronizer.get_duration_secs_from_ticks(
                        note.start_pos, note.end_pos
                    )
                    for seq_attr in vsqx_note.note_style.seq_attr:
                        if seq_attr.seq_id == "vibRate":
                            phase = 0
                            for prev_elem, elem in more_itertools.windowed(
                                [*seq_attr.elem, None], 2
                            ):
                                prev_start = start_secs + duration_secs * prev_elem.pos_nrm / 65536
                                omega = prev_elem.elv / 2
                                if elem is None:
                                    prev_end = start_secs + duration_secs
                                    vibrato_rate_interval_dict[
                                        portion.closed(prev_start, prev_end)
                                    ] = functools.partial(
                                        self.vibrato_curve,
                                        shift=prev_start,
                                        omega=omega,
                                        phase=phase,
                                    )
                                else:
                                    prev_end = start_secs + duration_secs * elem.pos_nrm / 65536
                                    vibrato_rate_interval_dict[
                                        portion.closedopen(prev_start, prev_end)
                                    ] = functools.partial(
                                        self.vibrato_curve,
                                        shift=prev_start,
                                        omega=omega,
                                        phase=phase,
                                    )
                                phase += (prev_end - prev_start) * omega
                        elif seq_attr.seq_id == "vibDep":
                            for prev_elem, elem in more_itertools.windowed(
                                [*seq_attr.elem, None], 2
                            ):
                                prev_start = start_secs + duration_secs * prev_elem.pos_nrm / 65536
                                if elem is None:
                                    prev_end = start_secs + duration_secs
                                    vibrato_depth_interval_dict[
                                        portion.closed(prev_start, prev_end)
                                    ] = prev_elem.elv
                                else:
                                    prev_end = start_secs + duration_secs * elem.pos_nrm / 65536
                                    vibrato_depth_interval_dict[
                                        portion.closedopen(prev_start, prev_end)
                                    ] = prev_elem.elv
                if (
                    prev_vsqx_note is not None
                    and prev_vsqx_note.phnms is not None
                    and prev_vsqx_note.pos_tick + prev_vsqx_note.dur_tick == vsqx_note.pos_tick
                    and prev_vsqx_note.phnms.value == "Sil"
                ):
                    note.head_tag = "0"
                note_list.append(note)
            prev_vsqx_note = vsqx_note
        if self.options.combine_syllables:
            for syllables_group in more_itertools.split_when(
                note_list,
                lambda prev_vsqx_note, vsqx_note: not prev_vsqx_note.lyric.endswith("-"),
            ):
                if len(syllables_group) > 1:
                    syllables_group[0].lyric = "".join(
                        vsqx_note.lyric.rstrip("-") for vsqx_note in syllables_group
                    )
                    for vsqx_note in syllables_group[1:]:
                        if vsqx_note.lyric != "-":
                            vsqx_note.lyric = "+"
        return (
            note_list,
            vibrato_rate_interval_dict,
            vibrato_depth_interval_dict,
        )

    def parse_pitch(
        self,
        musical_part: VsqxMusicalPart,
        note_list: list[Note],
        vibrato_rate_interval_dict: PiecewiseIntervalDict,
        vibrato_depth_interval_dict: PiecewiseIntervalDict,
        tick_offset: int,
    ) -> Optional[ParamCurve]:
        pitch_data = VocaloidPartPitchData(
            start_pos=musical_part.pos_tick - tick_offset,
            pit=[
                ControllerEvent(
                    pos=music_control.pos_tick,
                    value=music_control.attr.value,
                )
                for music_control in musical_part.m_ctrl
                if music_control.attr.type_param_attr_id == self.param_names.PIT.value
                and music_control.attr.value is not None
            ],
            pbs=[
                ControllerEvent(
                    pos=music_control.pos_tick,
                    value=music_control.attr.value,
                )
                for music_control in musical_part.m_ctrl
                if music_control.attr.type_param_attr_id == self.param_names.PBS.value
                and music_control.attr.value is not None
            ],
        )
        return pitch_from_vocaloid_parts(
            [pitch_data],
            self.synchronizer,
            note_list,
            vibrato_rate_interval_dict,
            vibrato_depth_interval_dict,
            self.first_bar_length,
            musical_part.pos_tick - tick_offset,
            musical_part.pos_tick + musical_part.play_time - tick_offset,
        )

    def parse_instrumental_tracks(
        self,
        wav_parts: VsqxWavPartList,
        wav_units: VsqxWavUnitList,
        tick_prefix: int,
    ) -> list[InstrumentalTrack]:
        instrumental_tracks = []
        if self.options.import_instrumental_track:
            for wav_part, wav_unit in zip(wav_parts, wav_units):
                if pathlib.Path(wav_part.file_path).is_absolute():
                    wav_path_str = wav_part.file_path
                elif (
                    wav_path := self.src_path.with_suffix(".wavparts") / wav_part.file_path
                ).exists():
                    wav_path_str = str(wav_path)
                else:
                    continue
                instrumental_tracks.append(
                    InstrumentalTrack(
                        title=wav_part.part_name,
                        audio_file_path=wav_path_str,
                        offset=wav_part.pos_tick - tick_prefix,
                        mute=wav_unit.mute,
                        solo=wav_unit.solo,
                    )
                )
        return instrumental_tracks
