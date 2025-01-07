import dataclasses
import pathlib

from libresvip.model.base import (
    InstrumentalTrack,
    Note,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
    Track,
)

from .model import (
    VOXFactoryAudioTrack,
    VOXFactoryNote,
    VOXFactoryProject,
    VOXFactoryVocalClip,
)
from .options import InputOptions


@dataclasses.dataclass
class VOXFactoryParser:
    options: InputOptions
    path: pathlib.Path

    def parse_project(self, vox_project: VOXFactoryProject) -> Project:
        project = Project(
            song_tempo_list=self.parse_tempos(vox_project.tempo),
            time_signature_list=self.parse_time_signatures(vox_project.time_signature),
            track_list=self.parse_tracks(vox_project),
        )
        return project

    def parse_tempos(self, tempo: float) -> list[SongTempo]:
        return [
            SongTempo(
                bpm=tempo,
                position=0,
            )
        ]

    def parse_time_signatures(self, time_signatures: list[int]) -> list[TimeSignature]:
        return [
            TimeSignature(
                bar_index=0,
                numerator=time_signatures[0],
                denominator=time_signatures[1],
            )
        ]

    def parse_tracks(self, vox_project: VOXFactoryProject) -> list[Track]:
        tracks = []
        for track_name, track_data in sorted(
            vox_project.track_bank.items(),
            key=lambda x: vox_project.track_order.index(x[0]),
        ):
            if isinstance(track_data, VOXFactoryAudioTrack):
                if self.options.import_instrumental_track:
                    for _, clip_data in sorted(
                        track_data.clip_bank.items(),
                        key=lambda x: track_data.clip_order.index(x[0]),
                    ):
                        track = InstrumentalTrack(
                            title=clip_data.name,
                            solo=track_data.solo,
                            mute=track_data.mute,
                            pan=track_data.pan,
                            audio_file_path=str(
                                (self.path.parent / clip_data.name).with_suffix(
                                    pathlib.Path(clip_data.source_audio_data_key).suffix
                                )
                            ),
                        )
                        tracks.append(track)
            else:
                note_list = []
                for _, clip_data in sorted(
                    track_data.clip_bank.items(),
                    key=lambda x: track_data.clip_order.index(x[0]),
                ):
                    note_list.extend(self.parse_notes(clip_data))
                if not note_list:
                    continue
                track = SingingTrack(
                    title=track_name,
                    solo=track_data.solo,
                    mute=track_data.mute,
                    pan=track_data.pan,
                    note_list=note_list,
                )
                tracks.append(track)
        return tracks

    def parse_notes(self, clip_data: VOXFactoryVocalClip) -> list[Note]:
        return [
            self.parse_note(note_data)
            for _, note_data in sorted(
                clip_data.note_bank.items(),
                key=lambda x: clip_data.note_order.index(x[0]),
            )
        ]

    def parse_note(self, note_data: VOXFactoryNote) -> Note:
        return Note(
            start_pos=int(note_data.ticks),
            length=int(note_data.duration_ticks),
            key_number=note_data.midi,
            lyric=note_data.name,
            pronunciation=note_data.syllable,
        )
