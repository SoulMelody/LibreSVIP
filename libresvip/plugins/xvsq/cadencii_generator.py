import dataclasses

from libresvip.core.tick_counter import shift_beat_list, skip_tempo_list
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
from libresvip.utils.binary.midi import bpm2tempo

from .model import (
    BgmFile,
    IconHandle,
    Lyric,
    LyricHandle,
    TempoTableEntry,
    TimeSigTableEntry,
    VibratoBPPair,
    VsqEvent,
    VsqEvents,
    VsqFileEx,
    VsqID,
    VsqIDType,
    VsqMetaText,
    VsqMixerEntry,
    VsqTrack,
)
from .options import OutputOptions
from .vocaloid_pitch import generate_for_vocaloid


@dataclasses.dataclass
class CadenciiGenerator:
    options: OutputOptions
    first_bar_length: int = dataclasses.field(init=False)
    time_synchronizer: TimeSynchronizer = dataclasses.field(init=False)
    time_signatures: list[TimeSignature] = dataclasses.field(init=False)

    def generate_project(self, project: Project) -> VsqFileEx:
        self.time_synchronizer = TimeSynchronizer(project.song_tempo_list)
        self.time_signatures = project.time_signature_list
        self.first_bar_length = tick_prefix = round(project.time_signature_list[0].bar_length())
        vsq_file = VsqFileEx()
        vsq_file.timesig_table.time_sig_table_entry.extend(
            self.generate_time_signatures(project.time_signature_list, vsq_file.master.pre_measure)
        )
        vsq_file.tempo_table.tempo_table_entry.extend(
            self.generate_tempos(project.song_tempo_list, tick_prefix)
        )
        vsq_file.bgm_files.bgm_file.extend(
            self.generate_instrumental_tracks(
                [track for track in project.track_list if isinstance(track, InstrumentalTrack)]
            )
        )
        vsq_file.track.vsq_track, vsq_file.mixer.slave.vsq_mixer_entry = (
            self.generate_singing_tracks(
                [track for track in project.track_list if isinstance(track, SingingTrack)],
                tick_prefix,
            )
        )
        vsq_file.total_clocks = max(
            (
                note.end_pos + tick_prefix
                for track in project.track_list
                for note in track.note_list
                if isinstance(track, SingingTrack)
            ),
            default=0,
        )
        return vsq_file

    def generate_tempos(
        self, tempo_list: list[SongTempo], tick_prefix: int
    ) -> list[TempoTableEntry]:
        tempo_list = skip_tempo_list(tempo_list, tick_prefix)
        return [
            TempoTableEntry(
                clock=tempo.position,
                tempo=bpm2tempo(tempo.bpm),
                time=tempo.position * 2 / self.first_bar_length,
            )
            for tempo in tempo_list
        ]

    def generate_time_signatures(
        self, time_signature_list: list[TimeSignature], measure_prefix: int
    ) -> list[TimeSigTableEntry]:
        time_signatures = shift_beat_list(time_signature_list, measure_prefix)
        time_sig_table_entry = []
        ticks = 0.0
        prev_time_signature = None
        for time_signature in time_signatures:
            if prev_time_signature is not None:
                bar_index = prev_time_signature.bar_index
                ticks += prev_time_signature.bar_length() * (time_signature.bar_index - bar_index)
            else:
                bar_index = 0
            time_sig_table_entry.append(
                TimeSigTableEntry(
                    clock=int(ticks),
                    bar_count=time_signature.bar_index - bar_index,
                    numerator=time_signature.numerator,
                    denominator=time_signature.denominator,
                )
            )
            prev_time_signature = time_signature
        return time_sig_table_entry

    def generate_notes(self, notes: list[Note], tick_prefix: int) -> list[VsqEvent]:
        vsq_events = []
        for internal_id, note in enumerate(notes, start=1):
            vsq_event = VsqEvent(
                internal_id=internal_id,
                clock=note.start_pos + tick_prefix,
                id=VsqID(
                    type_value=VsqIDType.ANOTE,
                    note=note.key_number,
                    length=note.end_pos - note.start_pos,
                ),
            )
            vsq_event.id.lyric_handle = LyricHandle(
                l0=Lyric(
                    phrase=note.lyric,
                )
            )
            vsq_events.append(vsq_event)
        return vsq_events

    def generate_instrumental_tracks(
        self, instrumental_tracks: list[InstrumentalTrack]
    ) -> list[BgmFile]:
        bgm_files = []
        for track in instrumental_tracks:
            bgm_file = BgmFile(
                file=track.audio_file_path,
                read_offset_seconds=self.time_synchronizer.get_actual_secs_from_ticks(track.offset),
            )
            bgm_files.append(bgm_file)
        return bgm_files

    def generate_singing_tracks(
        self, singing_tracks: list[SingingTrack], tick_prefix: int
    ) -> tuple[list[VsqTrack], list[VsqMixerEntry]]:
        vsq_tracks = [VsqTrack()]
        vsq_mixer_entries = []
        for track in singing_tracks:
            meta_text = VsqMetaText()
            meta_text.common.name = track.title
            meta_text.events.events = VsqEvents()
            meta_text.events.events.vsq_event.append(
                VsqEvent(
                    internal_id=0,
                    clock=0,
                    id=VsqID(
                        type_value=VsqIDType.SINGER,
                        icon_handle=IconHandle(
                            ids=track.ai_singer_name,
                        ),
                        note=0,
                        length=0,
                    ),
                )
            )
            meta_text.events.events.vsq_event.extend(
                self.generate_notes(track.note_list, tick_prefix)
            )
            self.generate_pitch(track.edited_params.pitch, track.note_list, meta_text, tick_prefix)
            vsq_track = VsqTrack(meta_text=meta_text)
            mixer_entry = VsqMixerEntry(
                solo=1 if track.solo else 0,
                mute=1 if track.mute else 0,
            )
            vsq_tracks.append(vsq_track)
            vsq_mixer_entries.append(mixer_entry)
        return vsq_tracks, vsq_mixer_entries

    def generate_pitch(
        self, pitch: ParamCurve, notes: list[Note], meta_text: VsqMetaText, tick_prefix: int
    ) -> None:
        if pitch_raw_data := generate_for_vocaloid(
            pitch, notes, self.time_signatures, self.first_bar_length, self.time_synchronizer
        ):
            meta_text.pbs.points = [
                VibratoBPPair(
                    x=pbs_event.pos + tick_prefix,
                    y=pbs_event.value,
                )
                for pbs_event in pitch_raw_data.pbs
            ]
            meta_text.pit.points = [
                VibratoBPPair(
                    x=pit_event.pos + tick_prefix,
                    y=pit_event.value,
                )
                for pit_event in pitch_raw_data.pit
            ]
