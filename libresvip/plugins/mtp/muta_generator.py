import dataclasses

from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import (
    InstrumentalTrack,
    Note,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
)
from libresvip.utils import audio_track_info

from .model import (
    MutaAudioTrackData,
    MutaNote,
    MutaParams,
    MutaProject,
    MutaSongTrackData,
    MutaTempo,
    MutaTimeSignature,
    MutaTrack,
    MutaTrackType,
)
from .options import OutputOptions


@dataclasses.dataclass
class MutaGenerator:
    options: OutputOptions
    time_synchronizer: TimeSynchronizer = dataclasses.field(init=False)

    def generate_project(self, project: Project) -> MutaProject:
        self.time_synchronizer = TimeSynchronizer(project.song_tempo_list)
        time_signatures = self.generate_time_signatures(project.time_signature_list)
        tempos = self.generate_tempos(project.song_tempo_list)
        singing_tracks = self.generate_singing_tracks(
            [track for track in project.track_list if isinstance(track, SingingTrack)]
        )
        instrumental_tracks = self.generate_instrumental_tracks(
            [
                track
                for track in project.track_list
                if isinstance(track, InstrumentalTrack)
            ],
            len(singing_tracks),
        )

        return MutaProject(
            file_version=101,
            time_signatures=time_signatures,
            tempos=tempos,
            tracks=singing_tracks + instrumental_tracks,
        )

    def generate_time_signatures(
        self, time_signatures: list[TimeSignature]
    ) -> list[MutaTimeSignature]:
        return [
            MutaTimeSignature(
                measure_position=time_signature.bar_index,
                numerator=time_signature.numerator,
                denominator=time_signature.denominator,
            )
            for time_signature in time_signatures
        ]

    def generate_tempos(self, tempos: list[SongTempo]) -> list[MutaTempo]:
        return [
            MutaTempo(
                position=tempo.position,
                bpm=round(tempo.bpm * 100),
            )
            for tempo in tempos
        ]

    def generate_singing_tracks(self, tracks: list[SingingTrack]) -> list[MutaTrack]:
        track_list = []
        for track in tracks:
            muta_track = MutaTrack(
                track_type=MutaTrackType.SONG,
                track_index=len(track_list) + 1,
                name=f"Song{len(track_list) + 1}",
                mute=track.mute,
                solo=track.solo,
                volume=50,
                pan=50,
                padding=b"\x00" * 52 + b"\n",
                talk_track_data=None,
                song_track_data=MutaSongTrackData(
                    start=0,
                    length=max((note.end_pos for note in track.note_list), default=0),
                    singer_name=[ord(c) for c in self.options.default_singer_name]
                    + [0] * (258 - len(self.options.default_singer_name)),
                    unknown_1=0,
                    notes=self.generate_notes(track.note_list),
                    params=MutaParams(
                        unknown_param=[],
                        pitch_range=[],
                        pitch_data=[],
                        volume_data=[],
                        vibrato_amplitude_range=[],
                        vibrato_amplitude_data=[],
                        vibrato_frequency_range=[],
                        vibrato_frequency_data=[],
                    ),
                ),
            )
            track_list.append(muta_track)
        return track_list

    def generate_notes(self, notes: list[Note]) -> list[MutaNote]:
        return [
            MutaNote(
                start=note.start_pos,
                length=note.length,
                key=139 - note.key_number,
                lyric=[ord(c) for c in note.lyric] + [0] * (8 - len(note.lyric)),
                phoneme=note.pronunciation or "",
                tmg_data=b"\x00" * 40,
            )
            for note in notes
        ]

    def generate_instrumental_tracks(
        self, tracks: list[InstrumentalTrack], singing_track_count: int
    ) -> list[MutaTrack]:
        track_list = []
        for track in tracks:
            if (
                track_info := audio_track_info(track.audio_file_path, only_wav=True)
            ) is not None:
                muta_track = MutaTrack(
                    track_type=MutaTrackType.AUDIO,
                    track_index=len(track_list) + 1 + singing_track_count,
                    name=f"Audio{len(track_list) + 1}",
                    mute=track.mute,
                    solo=track.solo,
                    volume=50,
                    pan=50,
                    padding=b"\x00" * 52 + b"\n",
                    talk_track_data=None,
                    song_track_data=None,
                )
                muta_track.audio_track_data = MutaAudioTrackData(
                    start=track.offset,
                    length=round(
                        self.time_synchronizer.get_actual_ticks_from_secs_offset(
                            track.offset, track_info.duration / 1000
                        )
                    ),
                    file_path=track.audio_file_path + "\0",
                )
                track_list.append(muta_track)
        return track_list
