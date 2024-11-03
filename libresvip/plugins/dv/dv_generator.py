import dataclasses
from typing import cast

from construct_typed import DataclassMixin, DataclassStruct

from libresvip.core.lyric_phoneme.chinese import CHINESE_RE, get_pinyin_series
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
from libresvip.utils.audio import audio_track_info

from .constants import (
    DEFAULT_PHONEME_BYTES,
    DEFAULT_VOLUME,
    MIN_SEGMENT_LENGTH,
)
from .deepvocal_pitch import convert_note_key, generate_for_dv
from .model import (
    DvAudioInfo,
    DvAudioTrack,
    DvInnerProject,
    DvNote,
    DvNoteParameter,
    DvPoint,
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
    first_bar_length: int = dataclasses.field(init=False)
    time_synchronizer: TimeSynchronizer = dataclasses.field(init=False)

    def generate_project(self, project: Project) -> DvProject:
        self.first_bar_length = round(project.time_signature_list[0].bar_length())
        self.tick_prefix = round(4 * project.time_signature_list[0].bar_length())
        self.time_synchronizer = TimeSynchronizer(project.song_tempo_list)
        singing_tracks = self.generate_singing_tracks(
            [track for track in project.track_list if isinstance(track, SingingTrack)]
        )
        audio_tracks = self.generate_instrumental_tracks(
            [track for track in project.track_list if isinstance(track, InstrumentalTrack)]
        )
        return DvProject(
            inner_project=DvInnerProject(
                tracks=singing_tracks + audio_tracks,
                tempos=self.generate_tempos(project.song_tempo_list),
                time_signatures=self.generate_time_signatures(project.time_signature_list),
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
                    song_tempo if i > 0 else song_tempo.model_copy(update={"position": 0})
                    for i, song_tempo in enumerate(tempos)
                ],
                self.tick_prefix - self.first_bar_length,
            )
        ]

    def generate_instrumental_tracks(
        self, instrumental_tracks: list[InstrumentalTrack]
    ) -> list[DvTrack]:
        track_list = []
        for track in instrumental_tracks:
            if (track_info := audio_track_info(track.audio_file_path)) is not None:
                audio_info = DvAudioInfo(
                    path=track.audio_file_path,
                    name=track.title,
                    start=track.offset + self.tick_prefix,
                    length=round(
                        self.time_synchronizer.get_actual_ticks_from_secs_offset(
                            track.offset, track_info.duration / 1000
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
                        track_type=cast(DvTrackType, DvTrackType.AUDIO),
                        track_data=dv_track,
                    )
                )
        return track_list

    def generate_singing_tracks(self, singing_tracks: list[SingingTrack]) -> list[DvTrack]:
        track_list = []
        for track in singing_tracks:
            dv_notes = self.generate_notes(track.note_list)
            dv_segment = DvSegment(
                start=self.tick_prefix,
                name=track.title,
                singer_name=track.ai_singer_name,
                length=max(
                    (note.end_pos for note in track.note_list),
                    default=MIN_SEGMENT_LENGTH,
                ),
                notes=dv_notes,
                volume_data=[
                    DvPoint(x=-1, y=128),
                    DvPoint(x=307201, y=128),
                ],
                pitch_data=[
                    DvPoint(x=-1, y=-1),
                    DvPoint(x=307201, y=-1),
                ],
                unknown_1=[
                    DvPoint(x=-1, y=128),
                    DvPoint(x=307201, y=128),
                ],
                breath_data=[
                    DvPoint(x=-1, y=128),
                    DvPoint(x=307201, y=128),
                ],
                gender_data=[
                    DvPoint(x=-1, y=128),
                    DvPoint(x=307201, y=128),
                ],
                unknown_2=[
                    DvPoint(x=-1, y=128),
                    DvPoint(x=307201, y=128),
                ],
                unknown_3=[
                    DvPoint(x=-1, y=128),
                    DvPoint(x=307201, y=128),
                ],
            )
            if (
                dv_segment_pitch_raw_data := generate_for_dv(
                    self.first_bar_length,
                    track.edited_params.pitch,
                    track.note_list,
                )
            ) is not None:
                dv_segment.pitch_data = dv_segment_pitch_raw_data.data
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
                    track_type=cast(DvTrackType, DvTrackType.SINGING),
                    track_data=dv_track,
                )
            )
        return track_list

    def generate_notes(self, notes: list[Note]) -> list[DvNote]:
        return [
            DvNote(
                start=note.start_pos,
                length=note.length,
                key=cast(int, convert_note_key(note.key_number)),
                phoneme=cast(str, note.pronunciation)
                or (
                    note.lyric
                    if CHINESE_RE.search(note.lyric) is None
                    else next(iter(get_pinyin_series(note.lyric)), "")
                ),
                word=note.lyric,
                padding_1=0,
                vibrato=50,
                note_vibrato_data=DvNoteParameter(
                    amplitude_points=[
                        DvPoint(x=-1, y=0),
                        DvPoint(x=100001, y=0),
                    ],
                    frequency_points=[
                        DvPoint(x=-1, y=0),
                        DvPoint(x=100001, y=0),
                    ],
                    vibrato_points=[
                        DvPoint(x=0, y=0),
                        DvPoint(x=1124, y=0),
                    ],
                ),
                unknown_phonemes=DEFAULT_PHONEME_BYTES,
                ben_depth=0,
                ben_length=0,
                por_head=0,
                por_tail=0,
                timbre=-1,
                cross_lyric="",
                cross_timbre=-1,
            )
            for note in notes
        ]
