import dataclasses
from typing import Optional

from libresvip.core.constants import KEY_IN_OCTAVE
from libresvip.core.lyric_phoneme.japanese import is_kana, is_romaji
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.core.warning_types import show_warning
from libresvip.model.base import (
    InstrumentalTrack,
    Note,
    ParamCurve,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
)
from libresvip.utils.translation import gettext_lazy as _

from .constants import DEFAULT_PHONEME, OCTAVE_OFFSET, TICK_RATE
from .model import (
    VoiSonaAudioEventItem,
    VoiSonaAudioTrackItem,
    VoiSonaBeatItem,
    VoiSonaNoteItem,
    VoiSonaParameterItem,
    VoiSonaParametersItem,
    VoiSonaPointData,
    VoiSonaProject,
    VoiSonaScoreItem,
    VoiSonaSingingTrackItem,
    VoiSonaSongItem,
    VoiSonaSoundItem,
    VoiSonaTempoItem,
    VoiSonaTimeItem,
    VoiSonaTrack,
    VoiSonaTrackState,
)
from .options import OutputOptions
from .voisona_pitch import generate_for_voisona


@dataclasses.dataclass
class VoisonaGenerator:
    options: OutputOptions
    first_bar_length: int = dataclasses.field(init=False)
    time_synchronizer: TimeSynchronizer = dataclasses.field(init=False)

    def generate_project(self, project: Project) -> VoiSonaProject:
        voisona_project = VoiSonaProject()
        self.time_synchronizer = TimeSynchronizer(project.song_tempo_list)
        self.first_bar_length = int(project.time_signature_list[0].bar_length())
        default_time_signatures = self.generate_time_signatures(project.time_signature_list)
        default_tempos = self.generate_tempos(project.song_tempo_list)
        voisona_project.tracks.append(VoiSonaTrack())
        for i, track in enumerate(project.track_list):
            if track.mute:
                track_state = VoiSonaTrackState.MUTE
            elif track.solo:
                track_state = VoiSonaTrackState.SOLO
            else:
                track_state = VoiSonaTrackState.NONE
            if isinstance(track, InstrumentalTrack):
                audio_track = VoiSonaAudioTrackItem(
                    name=f"Audio{i}",
                    state=track_state,
                    audio_event=[
                        VoiSonaAudioEventItem(
                            path=track.audio_file_path,
                            offset=self.time_synchronizer.get_actual_secs_from_ticks(track.offset),
                        )
                    ],
                )
                voisona_project.tracks[0].track.append(audio_track)
            elif isinstance(track, SingingTrack):
                singing_track = VoiSonaSingingTrackItem(
                    name=f"Singer{i}",
                    state=track_state,
                )
                song_item = VoiSonaSongItem(
                    beat=[default_time_signatures],
                    tempo=[default_tempos],
                    score=[VoiSonaScoreItem(note=self.generate_notes(track.note_list))],
                )
                singing_track.plugin_data.state_information.song = [song_item]
                voisona_project.tracks[0].track.append(singing_track)
                if log_f0 := self.generate_pitch(
                    track.edited_params.pitch, project.song_tempo_list
                ):
                    singing_track.plugin_data.state_information.parameter = [
                        VoiSonaParametersItem(log_f0=[log_f0])
                    ]
        return voisona_project

    def generate_tempos(self, tempos: list[SongTempo]) -> VoiSonaTempoItem:
        return VoiSonaTempoItem(
            sound=[
                VoiSonaSoundItem(
                    clock=round(tempo.position * TICK_RATE) if i else 0,
                    tempo=tempo.bpm,
                )
                for i, tempo in enumerate(tempos)
            ]
        )

    def generate_time_signatures(self, time_signatures: list[TimeSignature]) -> VoiSonaBeatItem:
        beat = VoiSonaBeatItem(
            time=[
                VoiSonaTimeItem(
                    clock=0,
                    beats=time_signatures[0].numerator,
                    beat_type=time_signatures[0].denominator,
                )
            ]
        )
        tick = 0.0
        prev_time_signature = time_signatures[0]
        for time_signature in time_signatures[1:]:
            if time_signature.bar_index > prev_time_signature.bar_index:
                tick += (
                    time_signature.bar_index - prev_time_signature.bar_index
                ) * prev_time_signature.bar_length()
            beat.time.append(
                VoiSonaTimeItem(
                    clock=int(tick * TICK_RATE),
                    beats=time_signature.numerator,
                    beat_type=time_signature.denominator,
                )
            )
            prev_time_signature = time_signature
        return beat

    def generate_notes(self, notes: list[Note]) -> list[VoiSonaNoteItem]:
        voisona_notes = []
        for note in notes:
            lyric = note.lyric
            phoneme = ""
            if not is_kana(lyric) and not is_romaji(lyric):
                phoneme = DEFAULT_PHONEME
                msg_prefix = _("Unsupported lyric: ")
                show_warning(f"{msg_prefix} {lyric}")
            voisona_notes.append(
                VoiSonaNoteItem(
                    clock=int(note.start_pos * TICK_RATE),
                    duration=int(note.length * TICK_RATE),
                    lyric=note.lyric,
                    pitch_octave=note.key_number // KEY_IN_OCTAVE + OCTAVE_OFFSET,
                    pitch_step=note.key_number % KEY_IN_OCTAVE,
                    syllabic=0,
                    phoneme=phoneme,
                )
            )
        return voisona_notes

    def generate_pitch(
        self, pitch: ParamCurve, tempo_list: list[SongTempo]
    ) -> Optional[VoiSonaParameterItem]:
        if (data := generate_for_voisona(pitch, tempo_list, self.first_bar_length)) is not None:
            return VoiSonaParameterItem(
                length=data.length,
                data=[
                    VoiSonaPointData(
                        index=each.idx,
                        repeat=each.repeat,
                        value=each.value,
                    )
                    for each in data.events
                ],
            )
