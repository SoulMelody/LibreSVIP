import contextlib
import dataclasses

from construct_typed import DataclassMixin, DataclassStruct
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError

from libresvip.core.tick_counter import shift_beat_list, shift_tempo_list
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import (
    InstrumentalTrack,
    Note,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
)

from .constants import DEFAULT_PHONEME_BYTES, DEFAULT_VOLUME, NOTE_KEY_SUM
from .model import (
    DvAudioInfo,
    DvAudioTrack,
    DvInnerProject,
    DvNote,
    DvNoteParameter,
    DvProject,
    DvSegment,
    DvSingingTrack,
    DvTempo,
    DvTimeSignature,
    DvTrack,
    DvTrackType,
)
from .options import OutputOptions


def size_of_object(obj: DataclassMixin) -> int:
    return len(DataclassStruct(type(obj)).build(obj))


@dataclasses.dataclass
class DeepVocalGenerator:
    options: OutputOptions
    tick_prefix: int = dataclasses.field(init=False)
    time_synchronizer: TimeSynchronizer = dataclasses.field(init=False)

    def generate_project(self, project: Project) -> DvProject:
        self.tick_prefix = round(4 * project.time_signature_list[0].bar_length())
        self.time_synchronizer = TimeSynchronizer(project.song_tempo_list)
        singing_tracks = self.generate_singing_tracks(
            [track for track in project.track_list if isinstance(track, SingingTrack)]
        )
        audio_tracks = self.generate_instrumental_tracks(
            [
                track
                for track in project.track_list
                if isinstance(track, InstrumentalTrack)
            ]
        )
        return DvProject(
            inner_project=DvInnerProject(
                tracks=singing_tracks + audio_tracks,
                tempos=self.generate_tempos(project.song_tempo_list),
                time_signatures=self.generate_time_signatures(
                    project.time_signature_list
                ),
            )
        )

    def generate_time_signatures(
        self, time_signatures: list[TimeSignature]
    ) -> list[DvTimeSignature]:
        return [
            DvTimeSignature(
                measure_position=ts.bar_index,
                numerator=ts.numerator,
                denominator=ts.denominator,
            )
            for ts in shift_beat_list(
                [
                    time_sig if i > 0 else time_sig.model_copy(update={"bar_index": -3})
                    for i, time_sig in enumerate(time_signatures)
                ],
                1,
            )
        ]

    def generate_tempos(self, tempos: list[SongTempo]) -> list[DvTempo]:
        return [
            DvTempo(
                position=tempo.position,
                bpm=round(tempo.bpm * 100),
            )
            for tempo in shift_tempo_list(
                [
                    song_tempo
                    if i > 0
                    else song_tempo.model_copy(update={"position": 0})
                    for i, song_tempo in enumerate(tempos)
                ],
                self.tick_prefix,
            )
        ]

    def generate_instrumental_tracks(
        self, instrumental_tracks: list[InstrumentalTrack]
    ) -> list[DvTrack]:
        track_list = []
        for track in instrumental_tracks:
            with contextlib.suppress(CouldntDecodeError, FileNotFoundError):
                audio_segment = AudioSegment.from_file(track.audio_file_path)
                audio_info = DvAudioInfo(
                    path=track.audio_file_path,
                    name=track.title,
                    start=track.offset + self.tick_prefix,
                    length=round(
                        self.time_synchronizer.get_actual_ticks_from_secs_offset(
                            track.offset, audio_segment.duration_seconds
                        )
                    ),
                )
                dv_track = DvAudioTrack(
                    name=track.title,
                    mute=track.mute,
                    solo=track.solo,
                    volume=DEFAULT_VOLUME,
                    balance=0,
                    infos=[audio_info],
                )
                track_list.append(
                    DvTrack(
                        track_type=DvTrackType.AUDIO,
                        track_data=dv_track,
                    )
                )
        return track_list

    def generate_singing_tracks(
        self, singing_tracks: list[SingingTrack]
    ) -> list[DvTrack]:
        track_list = []
        for track in singing_tracks:
            dv_notes = self.generate_notes(track.note_list)
            dv_segment = DvSegment(
                start=self.tick_prefix,
                name=track.title,
                singer_name=track.ai_singer_name,
                length=max(max(note.end_pos for note in track.note_list), 1920),
                notes=dv_notes,
                volume_data=[],
                pitch_data=[],
                unknown_1=[],
                breath_data=[],
                gender_data=[],
                unknown_2=[],
                unknown_3=[],
            )
            dv_track = DvSingingTrack(
                name=track.title,
                mute=track.mute,
                solo=track.solo,
                volume=DEFAULT_VOLUME,
                balance=0,
                segments=[dv_segment],
            )
            track_list.append(
                DvTrack(
                    track_type=DvTrackType.SINGING,
                    track_data=dv_track,
                )
            )
        return track_list

    def generate_notes(self, notes: list[Note]) -> list[DvNote]:
        return [
            DvNote(
                start=note.start_pos,
                length=note.length,
                key=int(NOTE_KEY_SUM) - note.key_number,
                phoneme=note.pronunciation or "",
                word=note.lyric,
                padding_1=0,
                vibrato=50,
                note_vibrato_data=DvNoteParameter(
                    amplitude_points=[],
                    frequency_points=[],
                    vibrato_points=[],
                ),
                unknown_phonemes=DEFAULT_PHONEME_BYTES,
                ben_depth=8,
                ben_length=5,
                por_head=16,
                por_tail=16,
                timbre=-1,
                cross_lyric="",
                cross_timbre=-1,
            )
            for note in notes
        ]
