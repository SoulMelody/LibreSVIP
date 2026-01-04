import dataclasses
import pathlib

from libresvip.core.tick_counter import skip_beat_list, skip_tempo_list
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
from libresvip.utils.binary.midi import tempo2bpm

from .model import (
    BgmFile,
    TempoTableEntry,
    TimeSigTableEntry,
    VsqEvent,
    VsqFileEx,
    VsqIDType,
    VsqMixerEntry,
    VsqTrack,
)
from .options import InputOptions
from .vocaloid_pitch import (
    ControllerEvent,
    VocaloidPartPitchData,
    pitch_from_vocaloid_parts,
)


@dataclasses.dataclass
class CadenciiParser:
    options: InputOptions
    time_synchronizer: TimeSynchronizer = dataclasses.field(init=False)
    first_bar_length: int = dataclasses.field(init=False)

    def parse_project(self, vsq_file: VsqFileEx) -> Project:
        tick_prefix, self.time_signatures = self.parse_time_signatures(
            vsq_file.timesig_table.time_sig_table_entry, vsq_file.master.pre_measure
        )
        tempos = self.parse_tempos(vsq_file.tempo_table.tempo_table_entry, tick_prefix)
        self.time_synchronizer = TimeSynchronizer(tempos)
        singing_tracks = self.parse_singing_tracks(
            vsq_file.track.vsq_track[1:], vsq_file.mixer.slave.vsq_mixer_entry, tick_prefix
        )
        instrumental_tracks = self.parse_instrumental_tracks(
            vsq_file.bgm_files.bgm_file, tick_prefix
        )
        return Project(
            time_signature_list=self.time_signatures,
            song_tempo_list=tempos,
            track_list=singing_tracks + instrumental_tracks,
        )

    def parse_tempos(
        self, tempo_table_entries: list[TempoTableEntry], tick_prefix: int
    ) -> list[SongTempo]:
        tempo_list = [
            SongTempo(
                position=tempo.time,
                bpm=tempo2bpm(tempo.tempo),
            )
            for tempo in tempo_table_entries
        ]
        return skip_tempo_list(tempo_list, tick_prefix)

    def parse_time_signatures(
        self, time_signatures: list[TimeSigTableEntry], measure_prefix: int
    ) -> tuple[int, list[TimeSignature]]:
        bar_index = -measure_prefix
        time_signature_list = []
        for time_signature in time_signatures:
            bar_index += time_signature.bar_count
            ts_obj = TimeSignature(
                bar_index=bar_index,
                numerator=time_signature.numerator,
                denominator=time_signature.denominator,
            )
            time_signature_list.append(ts_obj)
        tick_prefix = 0
        measure = 0
        for time_sig in time_signature_list:
            measure_diff = time_sig.bar_index - measure
            tick_prefix += measure_diff * round(time_sig.bar_length())
            measure += time_sig.bar_index
        measure_diff = measure_prefix - measure
        tick_prefix += measure_diff * round(time_signature_list[-1].bar_length())
        self.first_bar_length = int(time_signature_list[0].bar_length())
        return int(tick_prefix), skip_beat_list(time_signature_list, measure_prefix)

    def parse_notes(
        self,
        vsq_events: list[VsqEvent],
        tick_prefix: int,
    ) -> tuple[str, list[Note]]:
        singer_name = ""
        note_list = []
        for vsq_event in vsq_events:
            if (
                vsq_event.id.type_value.value == VsqIDType.SINGER.value
                and vsq_event.id.icon_handle is not None
            ):
                singer_name = vsq_event.id.icon_handle.ids
            elif vsq_event.id.type_value.value == VsqIDType.ANOTE.value:
                if vsq_event.clock < tick_prefix:
                    continue
                note = Note(
                    start_pos=vsq_event.clock - tick_prefix,
                    length=vsq_event.id.length,
                    key_number=vsq_event.id.note,
                )
                if vsq_event.id.lyric_handle is not None:
                    note.lyric = vsq_event.id.lyric_handle.l0.phrase or ""
                    if vsq_event.id.lyric_handle.l0.phonetic_symbol_protected:
                        note.pronunciation = vsq_event.id.lyric_handle.l0.phonetic_symbol
                note_list.append(note)
        return singer_name, note_list

    def parse_singing_tracks(
        self, vsq_tracks: list[VsqTrack], mixer_entries: list[VsqMixerEntry], tick_prefix: int
    ) -> list[SingingTrack]:
        singing_tracks = []
        for vsq_track, mixer_entry in zip(vsq_tracks, mixer_entries):
            if vsq_track.meta_text is None or vsq_track.meta_text.events.events is None:
                continue
            singing_track = SingingTrack(
                title=vsq_track.meta_text.common.name,
                solo=mixer_entry.solo == 1,
                mute=mixer_entry.mute == 1,
            )
            singer_name, notes = self.parse_notes(
                vsq_track.meta_text.events.events.vsq_event, tick_prefix
            )
            singing_track.ai_singer_name = singer_name
            singing_track.note_list = notes
            if self.options.import_pitch and (
                pitch := self.parse_pitch(vsq_track, singing_track.note_list, tick_prefix)
            ):
                singing_track.edited_params.pitch = pitch
            singing_tracks.append(singing_track)
        return singing_tracks

    def parse_pitch(
        self,
        vsq_track: VsqTrack,
        note_list: list[Note],
        tick_prefix: int,
    ) -> ParamCurve | None:
        pit: list[ControllerEvent] = []
        pbs: list[ControllerEvent] = []
        if vsq_track.meta_text is not None:
            pit.extend(
                ControllerEvent(
                    pos=int(point.x) - tick_prefix,
                    value=point.y,
                )
                for point in vsq_track.meta_text.pit.points
            )
            pbs.extend(
                ControllerEvent(
                    pos=int(point.x) - tick_prefix,
                    value=point.y,
                )
                for point in vsq_track.meta_text.pbs.points
            )
        return pitch_from_vocaloid_parts(
            [
                VocaloidPartPitchData(
                    start_pos=0,
                    pit=pit,
                    pbs=pbs,
                )
            ],
            self.time_synchronizer,
            note_list,
            self.time_signatures,
            self.first_bar_length,
        )

    def parse_instrumental_tracks(
        self, bgm_files: list[BgmFile], tick_prefix: int
    ) -> list[InstrumentalTrack]:
        instrumental_tracks = []
        if self.options.import_instrumental_track:
            for bgm_file in bgm_files:
                if not bgm_file.file:
                    continue
                offset_ticks = self.time_synchronizer.get_actual_ticks_from_secs_offset(
                    0 if bgm_file.start_after_premeasure else -tick_prefix,
                    bgm_file.read_offset_seconds,
                )
                instrumental_track = InstrumentalTrack(
                    title=pathlib.Path(bgm_file.file).stem,
                    audio_file_path=bgm_file.file,
                    offset=int(offset_ticks),
                    mute=bgm_file.mute == 1,
                )
                instrumental_tracks.append(instrumental_track)
        return instrumental_tracks
