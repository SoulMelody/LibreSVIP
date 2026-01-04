import dataclasses

from libresvip.core.constants import KEY_IN_OCTAVE
from libresvip.core.lyric_phoneme.japanese import is_kana, is_romaji
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.core.warning_types import show_warning
from libresvip.model.base import (
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
    VoiSonaMobileBeatItem,
    VoiSonaMobileNoteItem,
    VoiSonaMobileParameterItem,
    VoiSonaMobileParametersItem,
    VoiSonaMobilePointData,
    VoiSonaMobileProject,
    VoiSonaMobileScoreItem,
    VoiSonaMobileSinger,
    VoiSonaMobileSongItem,
    VoiSonaMobileSoundItem,
    VoiSonaMobileTempoItem,
    VoiSonaMobileTimeItem,
)
from .options import OutputOptions
from .voisona_mobile_pitch import generate_for_voisona


@dataclasses.dataclass
class VoiSonaMobileGenerator:
    options: OutputOptions
    first_bar_length: int = dataclasses.field(init=False)
    time_synchronizer: TimeSynchronizer = dataclasses.field(init=False)

    def generate_project(self, project: Project) -> VoiSonaMobileProject:
        if self.options.track_index < 0:
            first_singing_track = next(
                (
                    track
                    for track in project.track_list
                    if isinstance(track, SingingTrack) and track.note_list
                ),
                None,
            )
        else:
            first_singing_track = project.track_list[self.options.track_index]
            assert isinstance(first_singing_track, SingingTrack)
        voisona_project = VoiSonaMobileProject()
        self.time_synchronizer = TimeSynchronizer(project.song_tempo_list)
        self.first_bar_length = int(project.time_signature_list[0].bar_length())
        default_time_signatures = self.generate_time_signatures(project.time_signature_list)
        default_tempos = self.generate_tempos(project.song_tempo_list)
        if first_singing_track is not None:
            singing_track = VoiSonaMobileSinger()
            song_item = VoiSonaMobileSongItem(
                beat=[default_time_signatures],
                tempo=[default_tempos],
                score=[
                    VoiSonaMobileScoreItem(note=self.generate_notes(first_singing_track.note_list))
                ],
            )
            singing_track.mobile_singer_data.state_information.song = [song_item]
            voisona_project.mobile_singer.append(singing_track)
            if log_f0 := self.generate_pitch(
                first_singing_track.edited_params.pitch, project.song_tempo_list
            ):
                singing_track.mobile_singer_data.state_information.parameter = [
                    VoiSonaMobileParametersItem(log_f0=[log_f0])
                ]
        return voisona_project

    def generate_tempos(self, tempos: list[SongTempo]) -> VoiSonaMobileTempoItem:
        return VoiSonaMobileTempoItem(
            sound=[
                VoiSonaMobileSoundItem(
                    clock=round(tempo.position * TICK_RATE) if i else 0,
                    tempo=tempo.bpm,
                )
                for i, tempo in enumerate(tempos)
            ]
        )

    def generate_time_signatures(
        self, time_signatures: list[TimeSignature]
    ) -> VoiSonaMobileBeatItem:
        beat = VoiSonaMobileBeatItem(
            time=[
                VoiSonaMobileTimeItem(
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
                VoiSonaMobileTimeItem(
                    clock=int(tick * TICK_RATE),
                    beats=time_signature.numerator,
                    beat_type=time_signature.denominator,
                )
            )
            prev_time_signature = time_signature
        return beat

    def generate_notes(self, notes: list[Note]) -> list[VoiSonaMobileNoteItem]:
        voisona_notes = []
        for note in notes:
            lyric = note.lyric
            phoneme = ""
            if note.pronunciation:
                phoneme = note.pronunciation
            elif not is_kana(lyric) and not is_romaji(lyric):
                phoneme = DEFAULT_PHONEME
                msg_prefix = _("Unsupported lyric: ")
                show_warning(f"{msg_prefix} {lyric}")
            voisona_notes.append(
                VoiSonaMobileNoteItem(
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
    ) -> VoiSonaMobileParameterItem | None:
        if (data := generate_for_voisona(pitch, tempo_list, self.first_bar_length)) is not None:
            return VoiSonaMobileParameterItem(
                length=data.length,
                data=[
                    VoiSonaMobilePointData(
                        index=each.idx,
                        repeat=each.repeat,
                        value=each.value,
                    )
                    for each in data.events
                ],
            )
