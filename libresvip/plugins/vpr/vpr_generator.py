import dataclasses
import pathlib
from typing import Optional

from libresvip.core.constants import TICKS_IN_BEAT
from libresvip.core.lyric_phoneme.chinese import get_pinyin_series
from libresvip.core.lyric_phoneme.chinese.vocaloid_xsampa import pinyin2xsampa
from libresvip.core.lyric_phoneme.japanese import to_romaji
from libresvip.core.lyric_phoneme.japanese.vocaloid_xsampa import (
    legato_chars,
    romaji2xsampa,
)
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.core.warning_types import show_warning
from libresvip.model.base import (
    InstrumentalTrack,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
    Track,
)
from libresvip.utils.audio import audio_track_info
from libresvip.utils.translation import gettext_lazy as _

from .constants import (
    BPM_RATE,
    DEFAULT_CHINESE_PHONEME,
    DEFAULT_JAPANESE_PHONEME,
    PITCH_BEND_NAME,
    PITCH_BEND_SENSITIVITY_NAME,
)
from .model import (
    VocaloidAITrack,
    VocaloidAIVoice,
    VocaloidAudioTrack,
    VocaloidControllers,
    VocaloidLangID,
    VocaloidLanguage,
    VocaloidNotes,
    VocaloidPoint,
    VocaloidProject,
    VocaloidRegion,
    VocaloidStandardTrack,
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
    first_bar_length: int = dataclasses.field(init=False)
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
        self.first_bar_length = round(project.time_signature_list[0].bar_length())
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
        output_tick = 0.0
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
        self.end_tick = max(self.end_tick, round(output_tick))
        return time_sig_events

    def generate_tempos(self, tempo_list: list[SongTempo]) -> list[VocaloidPoint]:
        tempo_events = [
            VocaloidPoint(pos=it.position, value=int(it.bpm * BPM_RATE)) for it in tempo_list
        ]
        self.end_tick = max(self.end_tick, max((it.pos for it in tempo_events), default=0))
        return tempo_events

    def generate_phoneme(self, lyric: str) -> str:
        if lyric in legato_chars:
            return "-"
        if self.options.default_lang_id == VocaloidLanguage.SIMPLIFIED_CHINESE:
            pinyin = " ".join(get_pinyin_series([lyric], filter_non_chinese=False))
            return pinyin2xsampa.get(pinyin, DEFAULT_CHINESE_PHONEME)
        elif self.options.default_lang_id == VocaloidLanguage.JAPANESE:
            return romaji2xsampa.get(to_romaji(lyric), DEFAULT_JAPANESE_PHONEME)
        return DEFAULT_CHINESE_PHONEME

    def generate_tracks(self, track_list: list[Track]) -> list[VocaloidTracks]:
        tracks: list[VocaloidTracks] = []
        singing_track_found = False
        for track in track_list:
            if isinstance(track, InstrumentalTrack):
                wav_path = pathlib.Path(track.audio_file_path)
                if (
                    (track_info := audio_track_info(track.audio_file_path, only_wav=True))
                    is not None
                    and track_info.sampling_rate == 44100
                    and track_info.bit_depth == 16
                ):
                    audio_duration_in_secs = track_info.duration / 1000
                    wav_part_region_end = self.time_synchronizer.get_actual_ticks_from_secs_offset(
                        track.offset, audio_duration_in_secs
                    )
                    self.wav_paths[wav_path.name] = wav_path
                    wav_part = VocaloidWavPart(
                        pos=track.offset,
                        wav=VocaloidWav(
                            original_name=wav_path.name,
                            name=wav_path.name,
                        ),
                        region=VocaloidRegion(
                            begin=0,
                            end=wav_part_region_end,
                        ),
                    )
                    self.end_tick = max(
                        self.end_tick,
                        int(wav_part_region_end),
                    )
                    tracks.append(
                        VocaloidAudioTrack(
                            name=track.title,
                            parts=[wav_part],
                            is_muted=track.mute,
                            is_solo_mode=track.solo,
                        )
                    )
            elif isinstance(track, SingingTrack):
                singing_track_found = True
                notes = [
                    VocaloidNotes(
                        pos=note.start_pos,
                        duration=note.length,
                        number=note.key_number,
                        lyric=note.lyric,
                        phoneme=self.generate_phoneme(note.lyric),
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
                            lang_ids=[VocaloidLangID(lang_id=self.options.default_lang_id)],
                        )
                    else:
                        part.voice = VocaloidVoice(
                            comp_id=self.options.default_comp_id,
                            lang_id=self.options.default_lang_id,
                        )
                vocaloid_track = (
                    VocaloidAITrack if self.options.is_ai_singer else VocaloidStandardTrack
                )(
                    name=track.title,
                    parts=[part] if part else [],
                    is_muted=track.mute,
                    is_solo_mode=track.solo,
                )
                vocaloid_track.panpot.events.append(VocaloidPoint(pos=0, value=0))
                tracks.append(vocaloid_track)
                if duration:
                    self.end_tick = max(
                        self.end_tick,
                        duration,
                    )
        if singing_track_found and self.options.default_lang_id not in [
            VocaloidLanguage.SIMPLIFIED_CHINESE,
            VocaloidLanguage.JAPANESE,
        ]:
            show_warning(
                _(
                    'Phonemes of all notes were set to "la". Please use "Job" -> "Convert Phonemes to Match Languages in the menu of VOCALOID to reset them.'
                )
            )
        return tracks

    def generate_pitch_data(self, track: SingingTrack) -> Optional[list[VocaloidControllers]]:
        raw_pitch_data = generate_for_vocaloid(
            track.edited_params.pitch,
            track.note_list,
            self.first_bar_length,
            self.time_synchronizer,
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
                VocaloidControllers(name=PITCH_BEND_SENSITIVITY_NAME, events=controller_events)
            )
        if raw_pitch_data.pit:
            controller_events = [
                VocaloidPoint(pos=pit_event.pos, value=pit_event.value)
                for pit_event in raw_pitch_data.pit
            ]
            controllers.append(VocaloidControllers(name=PITCH_BEND_NAME, events=controller_events))
        return controllers
