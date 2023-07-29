import dataclasses
import pathlib
from typing import Optional

from libresvip.core.constants import DEFAULT_PHONEME, TICKS_IN_BEAT
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import (
    InstrumentalTrack,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
    Track,
)
from libresvip.utils import audio_track_info

from .constants import BPM_RATE, PITCH_BEND_NAME, PITCH_BEND_SENSITIVITY_NAME
from .model import (
    VocaloidAIVoice,
    VocaloidControllers,
    VocaloidLangID,
    VocaloidNotes,
    VocaloidPoint,
    VocaloidProject,
    VocaloidRegion,
    VocaloidTimeSig,
    VocaloidTracks,
    VocaloidVoice,
    VocaloidVoicePart,
    VocaloidVoices,
    VocaloidWav,
    VocaloidWavPart,
)
from .options import OutputOptions
from .vocaloid_pitch import generate_for_vocaloid


@dataclasses.dataclass
class VocaloidGenerator:
    options: OutputOptions
    time_synchronizer: TimeSynchronizer = dataclasses.field(init=False)
    end_tick: int = 0
    wav_paths: dict[str, pathlib.Path] = dataclasses.field(default_factory=dict)

    def generate_project(self, project: Project) -> VocaloidProject:
        vpr = VocaloidProject(
            voices=[
                VocaloidVoices(
                    comp_id=self.options.default_comp_id,
                    name=self.options.default_singer_name,
                )
            ]
        )
        vpr.master_track.time_sig.events = self.generate_time_signatures(
            project.time_signature_list
        )
        vpr.master_track.tempo.events = self.generate_tempos(project.song_tempo_list)
        vpr.master_track.volume.events.append(VocaloidPoint(pos=0, value=0))
        self.time_synchronizer = TimeSynchronizer(project.song_tempo_list)
        vpr.tracks = self.generate_tracks(project.track_list)
        vpr.master_track.loop.end = self.end_tick
        return vpr

    def generate_time_signatures(
        self, time_signature_list: list[TimeSignature]
    ) -> list[VocaloidTimeSig]:
        output_tick = 0
        time_sig_events: list[VocaloidTimeSig] = []
        for time_signature in time_signature_list:
            if not time_sig_events:
                output_tick += TICKS_IN_BEAT * 4 * time_signature.bar_index
            else:
                output_tick += (
                    TICKS_IN_BEAT
                    * 4
                    * (time_sig_events[-1].numer / time_sig_events[-1].denom)
                    * (time_signature.bar_index - time_sig_events[-1].bar)
                )
            time_sig_events.append(
                VocaloidTimeSig(
                    bar=time_signature.bar_index,
                    denom=time_signature.denominator,
                    numer=time_signature.numerator,
                )
            )
        self.end_tick = max(self.end_tick, output_tick)
        return time_sig_events

    def generate_tempos(self, tempo_list: list[SongTempo]) -> list[VocaloidPoint]:
        tempo_events = [
            VocaloidPoint(pos=it.position, value=int(it.bpm * BPM_RATE))
            for it in tempo_list
        ]
        self.end_tick = max(
            self.end_tick, max((it.pos for it in tempo_events), default=0)
        )
        return tempo_events

    def generate_tracks(self, track_list: list[Track]) -> list[VocaloidTracks]:
        tracks: list[VocaloidTracks] = []
        for track in track_list:
            if isinstance(track, InstrumentalTrack):
                wav_path = pathlib.Path(track.audio_file_path)
                if (
                    track_info := audio_track_info(track.audio_file_path, only_wav=True)
                ) is not None:
                    audio_duration_in_secs = track_info.duration / 1000
                    audio_duration_in_ticks = (
                        self.time_synchronizer.get_actual_ticks_from_secs(
                            audio_duration_in_secs
                        )
                    )
                    self.wav_paths[wav_path.name] = wav_path
                    wav_part = VocaloidWavPart(
                        pos=track.offset,
                        wav=VocaloidWav(
                            original_name=wav_path.name,
                            name=wav_path.name,
                        ),
                        region=VocaloidRegion(
                            begin=track.offset,
                            end=track.offset + audio_duration_in_ticks,
                        ),
                    )
                    self.end_tick = max(
                        self.end_tick,
                        wav_part.region.end,
                    )
                    tracks.append(
                        VocaloidTracks(
                            name=track.title,
                            parts=[wav_part],
                            is_muted=track.mute,
                            is_solo_mode=track.solo,
                        )
                    )
            elif isinstance(track, SingingTrack):
                notes = [
                    VocaloidNotes(
                        pos=note.start_pos,
                        duration=note.length,
                        number=note.key_number,
                        lyric=note.lyric,
                        phoneme=note.pronunciation or DEFAULT_PHONEME,
                        lang_id=self.options.default_lang_id,
                    )
                    for note in track.note_list
                ]
                duration = track.note_list[-1].end_pos if track.note_list else None
                controllers = self.generate_pitch_data(track)
                part = (
                    VocaloidVoicePart(
                        duration=duration,
                        notes=notes,
                        controllers=controllers,
                    )
                    if duration
                    else None
                )
                if part is not None:
                    if self.options.is_ai_singer:
                        part.ai_voice = VocaloidAIVoice(
                            comp_id=self.options.default_comp_id,
                            lang_ids=[
                                VocaloidLangID(lang_id=self.options.default_lang_id)
                            ],
                        )
                    else:
                        part.voice = VocaloidVoice(
                            comp_id=self.options.default_comp_id,
                            lang_id=self.options.default_lang_id,
                        )
                track = VocaloidTracks(
                    name=track.title,
                    parts=[part] if part else [],
                    is_muted=track.mute,
                    is_solo_mode=track.solo,
                )
                track.panpot.events.append(VocaloidPoint(pos=0, value=0))
                tracks.append(track)
                if duration:
                    self.end_tick = max(
                        self.end_tick,
                        duration,
                    )
        return tracks

    @staticmethod
    def generate_pitch_data(track: SingingTrack) -> Optional[list[VocaloidControllers]]:
        raw_pitch_data = generate_for_vocaloid(
            track.edited_params.pitch, track.note_list
        )
        if not raw_pitch_data:
            return None
        controllers = []
        if raw_pitch_data.pbs:
            controller_events = [
                VocaloidPoint(pos=pbs_event.pos, value=pbs_event.value)
                for pbs_event in raw_pitch_data.pbs
            ]
            controllers.append(
                VocaloidControllers(
                    name=PITCH_BEND_SENSITIVITY_NAME, events=controller_events
                )
            )
        if raw_pitch_data.pit:
            controller_events = [
                VocaloidPoint(pos=pit_event.pos, value=pit_event.value)
                for pit_event in raw_pitch_data.pit
            ]
            controllers.append(
                VocaloidControllers(name=PITCH_BEND_NAME, events=controller_events)
            )
        return controllers
