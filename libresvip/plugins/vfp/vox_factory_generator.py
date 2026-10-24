import dataclasses
import math
import pathlib
import secrets

from libresvip.core.constants import DEFAULT_BPM, DEFAULT_PHONEME, TICKS_IN_BEAT
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import (
    InstrumentalTrack,
    Note,
    ParamCurve,
    Params,
    Project,
    SongTempo,
    TimeSignature,
    Track,
)
from libresvip.utils.audio import audio_track_info

from .model import (
    VOXFactoryAudioClip,
    VOXFactoryAudioData,
    VOXFactoryAudioTrack,
    VOXFactoryMaster,
    VOXFactoryNote,
    VoxFactoryPitchPoint,
    VOXFactoryProject,
    VOXFactoryTrack,
    VOXFactoryVocalClip,
    VOXFactoryVocalTrack,
)
from .options import OutputOptions

CLIP_LENGTH_QUARTERS = 32
PITCH_SAMPLE_TICKS = 20
DEFAULT_LOOP_LENGTH_QUARTERS = 16


@dataclasses.dataclass
class VOXFactoryGenerator:
    options: OutputOptions
    prefix: str = dataclasses.field(init=False)
    audio_paths: dict[str, pathlib.Path] = dataclasses.field(default_factory=dict)
    synchronizer: TimeSynchronizer = dataclasses.field(init=False)
    first_bar_length: int = dataclasses.field(init=False)

    def generate_project(self, project: Project) -> VOXFactoryProject:
        self.prefix = secrets.token_hex(5)
        self.first_bar_length = int(project.time_signature_list[0].bar_length())
        self.synchronizer = TimeSynchronizer(project.song_tempo_list)
        track_bank, audio_data_bank = self.generate_tracks(project.track_list)
        return VOXFactoryProject(
            tempo=self.generate_tempo(project.song_tempo_list),
            time_signature=self.generate_time_signature(project.time_signature_list),
            loop=[0, DEFAULT_LOOP_LENGTH_QUARTERS],
            master=VOXFactoryMaster(),
            track_bank=track_bank,
            track_order=sorted(track_bank.keys()),
            audio_data_bank=audio_data_bank,
        )

    def generate_tempo(self, tempos: list[SongTempo]) -> float:
        return tempos[0].bpm if tempos else DEFAULT_BPM

    def generate_time_signature(self, time_signatures: list[TimeSignature]) -> list[int]:
        if time_signatures:
            return [time_signatures[0].numerator, time_signatures[0].denominator]
        else:
            return [4, 4]

    def generate_tracks(
        self, tracks: list[Track]
    ) -> tuple[dict[str, VOXFactoryTrack], dict[str, VOXFactoryAudioData]]:
        track_bank = {}
        audio_data_bank = {}
        for i, track in enumerate(tracks):
            if isinstance(track, InstrumentalTrack):
                audio_path = pathlib.Path(track.audio_file_path)
                if (track_info := audio_track_info(track.audio_file_path)) is not None:
                    source_audio_data_key = f"{self.prefix}-au{i}{audio_path.suffix}"
                    self.audio_paths[source_audio_data_key] = audio_path
                    audio_data_bank[source_audio_data_key] = VOXFactoryAudioData(
                        sample_rate=track_info.sample_rate,
                        sample_length=int(track_info.duration * track_info.sample_rate),
                        number_of_channels=track_info.channels,
                    )
                    clip_bank = {
                        f"{self.prefix}-cl0": VOXFactoryAudioClip(
                            name=audio_path.stem,
                            offset_quarter=0,
                            start_quarter=track.offset / TICKS_IN_BEAT,
                            length=track_info.duration,
                            source_audio_data_key=source_audio_data_key,
                        )
                    }
                    clip_order = [f"{self.prefix}-cl0"]
                    track_bank[f"{self.prefix}-tr{i}"] = VOXFactoryAudioTrack(
                        clip_bank=clip_bank,
                        clip_order=clip_order,
                        name=track.title,
                        mute=track.mute,
                        solo=track.solo,
                        pan=track.pan,
                    )
            else:
                clip_bank = self.generate_notes(track.note_list, track.edited_params)
                clip_order = sorted(clip_bank.keys())
                track_bank[f"{self.prefix}-tr{i}"] = VOXFactoryVocalTrack(
                    clip_bank=clip_bank,
                    clip_order=clip_order,
                    name=track.title,
                    mute=track.mute,
                    solo=track.solo,
                    pan=track.pan,
                )
        return track_bank, audio_data_bank

    def generate_notes(self, notes: list[Note], params: Params) -> dict[str, VOXFactoryVocalClip]:
        note_bank = {
            f"{self.prefix}-no{i}": self.generate_note(note) for i, note in enumerate(notes)
        }
        note_keys = list(note_bank)
        pitch_samples = self.generate_pitch_samples(params.pitch)
        clip_span = CLIP_LENGTH_QUARTERS * TICKS_IN_BEAT
        max_ticks = max((note.end_pos for note in notes), default=0)
        clip_bank = {}
        for i in range(math.ceil(max_ticks / clip_span)):
            start_ticks = i * clip_span
            end_ticks = start_ticks + clip_span
            keys = [
                key
                for key, note in zip(note_keys, notes)
                if start_ticks <= note.start_pos < end_ticks
            ]
            pitch_bank, pitch_order = self.generate_pitch_points(
                pitch_samples, i, start_ticks, end_ticks
            )
            clip_bank[f"{self.prefix}-cl{i}"] = VOXFactoryVocalClip(
                start_quarter=CLIP_LENGTH_QUARTERS * i,
                offset_quarter=CLIP_LENGTH_QUARTERS * i,
                length=CLIP_LENGTH_QUARTERS,
                note_bank={key: note_bank[key] for key in keys},
                note_order=keys,
                pitch_point_bank=pitch_bank,
                pitch_point_order=pitch_order,
            )
        return clip_bank

    def generate_note(self, note: Note) -> VOXFactoryNote:
        return VOXFactoryNote(
            time=self.synchronizer.get_actual_secs_from_ticks(note.start_pos),
            duration=self.synchronizer.get_duration_secs_from_ticks(note.start_pos, note.end_pos),
            ticks=note.start_pos,
            duration_ticks=note.length,
            midi=note.key_number,
            name=note.lyric,
            syllable=note.pronunciation or DEFAULT_PHONEME,
        )

    def generate_pitch_samples(self, pitch: ParamCurve) -> list[tuple[int, float, bool]]:
        """Drawn pitch as `(song tick, semitone, connects to the next point)`.

        The app interpolates between adjacent pitch points only while the left
        one is `connected`, and a `-100` point in the internal curve marks a gap
        in the drawn line, so each run ends with a point that does not connect.
        """

        def close(run: list[tuple[int, float]]) -> list[tuple[int, float, bool]]:
            return [(tick, value, index < len(run) - 1) for index, (tick, value) in enumerate(run)]

        samples: list[tuple[int, float, bool]] = []
        run: list[tuple[int, float]] = []
        for point in pitch.reduce_sample_rate(PITCH_SAMPLE_TICKS, -100).points.root:
            tick = point.x - self.first_bar_length
            if point.y == -100 or tick < 0:
                if run:
                    samples.extend(close(run))
                    run = []
            else:
                run.append((tick, point.y / 100))
        if run:
            samples.extend(close(run))
        return samples

    def generate_pitch_points(
        self,
        samples: list[tuple[int, float, bool]],
        clip_index: int,
        start_ticks: int,
        end_ticks: int,
    ) -> tuple[dict[str, VoxFactoryPitchPoint], list[str]]:
        pitch_bank = {}
        pitch_order = []
        for tick, value, connected in samples:
            if not start_ticks <= tick < end_ticks:
                continue
            key = f"{self.prefix}-pp{clip_index}-{len(pitch_order)}"
            pitch_bank[key] = VoxFactoryPitchPoint(
                quarter=tick / TICKS_IN_BEAT,
                pitch=value,
                connected=connected,
            )
            pitch_order.append(key)
        return pitch_bank, pitch_order
