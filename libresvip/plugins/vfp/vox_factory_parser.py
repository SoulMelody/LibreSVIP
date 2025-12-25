import dataclasses
import pathlib

from libresvip.core.constants import TICKS_IN_BEAT
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import (
    InstrumentalTrack,
    Note,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
    Track,
)
from libresvip.model.point import Point

from .model import (
    VOXFactoryAudioTrack,
    VOXFactoryProject,
    VOXFactoryVocalClip,
)
from .options import InputOptions


@dataclasses.dataclass
class VOXFactoryParser:
    options: InputOptions
    path: pathlib.Path
    synchronizer: TimeSynchronizer = dataclasses.field(init=False)
    first_bar_length: int = dataclasses.field(init=False)

    def parse_project(self, vox_project: VOXFactoryProject) -> Project:
        return Project(
            song_tempo_list=self.parse_tempos(vox_project.tempo),
            time_signature_list=self.parse_time_signatures(vox_project.time_signature),
            track_list=self.parse_tracks(vox_project),
        )

    def parse_tempos(self, tempo: float) -> list[SongTempo]:
        tempos = [
            SongTempo(
                bpm=tempo,
                position=0,
            )
        ]
        self.synchronizer = TimeSynchronizer(tempos)
        return tempos

    def parse_time_signatures(self, time_signatures: list[int]) -> list[TimeSignature]:
        time_signature = TimeSignature(
            bar_index=0,
            numerator=time_signatures[0],
            denominator=time_signatures[1],
        )
        self.first_bar_length = int(time_signature.bar_length())
        return [time_signature]

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
                        if not clip_data.source_audio_data_key:
                            continue
                        audio_path = (self.path.parent / clip_data.name).with_suffix(
                            pathlib.Path(clip_data.source_audio_data_key).suffix
                        )
                        if audio_path.exists():
                            track = InstrumentalTrack(
                                title=clip_data.name,
                                solo=track_data.solo,
                                mute=track_data.mute,
                                pan=track_data.pan,
                                offset=int(
                                    TICKS_IN_BEAT
                                    * (clip_data.start_quarter - clip_data.offset_quarter)
                                ),
                                audio_file_path="",
                            )
                            tracks.append(track)
            else:
                note_list = []
                pitch_points = []
                for _, clip_data in sorted(
                    track_data.clip_bank.items(),
                    key=lambda x: track_data.clip_order.index(x[0]),
                ):
                    clip_offset = int(
                        TICKS_IN_BEAT * (clip_data.start_quarter - clip_data.offset_quarter)
                    )
                    clip_notes, clip_pitch_points = self.parse_notes(clip_data, clip_offset)
                    note_list.extend(clip_notes)
                    pitch_points.extend(clip_pitch_points)
                if not note_list:
                    continue
                track = SingingTrack(
                    title=track_name,
                    solo=track_data.solo,
                    mute=track_data.mute,
                    pan=track_data.pan,
                    note_list=note_list,
                )
                if self.options.import_pitch:
                    pitch_points.insert(0, Point.start_point())
                    pitch_points.append(Point.end_point())
                    track.edited_params.pitch.points.root = pitch_points
                tracks.append(track)
        return tracks

    def parse_notes(
        self, clip_data: VOXFactoryVocalClip, clip_offset: int
    ) -> tuple[list[Note], list[Point]]:
        notes: list[Note] = []
        pitch_points: list[Point] = []
        f0_secs_step = 1024 / 44100
        for _, note_data in sorted(
            clip_data.note_bank.items(),
            key=lambda x: clip_data.note_order.index(x[0]),
        ):
            note = Note(
                start_pos=int(note_data.ticks + clip_offset),
                length=int(note_data.duration_ticks),
                key_number=note_data.midi,
                lyric=note_data.name,
                pronunciation=note_data.syllable,
            )
            if notes and note.start_pos < notes[-1].end_pos:
                notes[-1].length = note.start_pos - notes[-1].start_pos
            if self.options.import_pitch and note_data.pitch_bends:
                pitch_start = int(note_data.ticks + clip_offset + (note_data.pre_bend or 0))
                note_pitch_points = [Point(x=pitch_start + self.first_bar_length, y=-100)]
                pitch_start_secs = self.synchronizer.get_actual_secs_from_ticks(pitch_start)
                pitch_end_secs = pitch_start_secs + f0_secs_step * len(note_data.pitch_bends)
                pitch_end = self.synchronizer.get_actual_ticks_from_secs(pitch_end_secs)
                pitch_step = (pitch_end - pitch_start) / len(note_data.pitch_bends)
                for i, pitch_bend in enumerate(note_data.pitch_bends):
                    note_pitch_points.append(
                        Point(
                            x=int(pitch_start + i * pitch_step) + self.first_bar_length,
                            y=int((note_data.midi + pitch_bend) * 100),
                        )
                    )
                note_pitch_points.append(Point(x=int(pitch_end) + self.first_bar_length, y=-100))
                pitch_points.extend(note_pitch_points)
            notes.append(note)
        return notes, pitch_points
