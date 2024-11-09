import dataclasses

from libresvip.core.constants import DEFAULT_JAPANESE_LYRIC
from libresvip.core.lyric_phoneme.japanese import is_kana
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.core.warning_types import show_warning
from libresvip.model.base import Note, Project, SingingTrack, SongTempo, TimeSignature
from libresvip.utils.text import uuid_str
from libresvip.utils.translation import gettext_lazy as _

from .model import (
    VoiceVoxNote,
    VoiceVoxProject,
    VoiceVoxSong,
    VoiceVoxTempo,
    VoiceVoxTimeSignature,
    VoiceVoxTrack,
)
from .options import OutputOptions


@dataclasses.dataclass
class VOICEVOXGenerator:
    options: OutputOptions
    first_bar_length: int = dataclasses.field(init=False)
    time_synchronizer: TimeSynchronizer = dataclasses.field(init=False)

    def generate_project(self, project: Project) -> VoiceVoxProject:
        self.time_synchronizer = TimeSynchronizer(project.song_tempo_list)
        self.first_bar_length = int(project.time_signature_list[0].bar_length())
        song = VoiceVoxSong(
            tempos=self.generate_tempos(project.song_tempo_list),
            time_signatures=self.generate_time_signatures(project.time_signature_list),
        )
        for track in project.track_list:
            if isinstance(track, SingingTrack):
                track_key = uuid_str()
                song.track_order.append(track_key)
                song.tracks[track_key] = self.generate_track(track)
        return VoiceVoxProject(song=song)

    def generate_time_signatures(
        self, time_signature_list: list[TimeSignature]
    ) -> list[VoiceVoxTimeSignature]:
        return [
            VoiceVoxTimeSignature(
                measure_number=time_signature.bar_index + 1,
                beats=time_signature.numerator,
                beat_type=time_signature.denominator,
            )
            for time_signature in time_signature_list[:1]
        ]

    def generate_tempos(self, tempo_list: list[SongTempo]) -> list[VoiceVoxTempo]:
        return [
            VoiceVoxTempo(bpm=round(tempo.bpm), position=tempo.position) for tempo in tempo_list
        ]

    def generate_track(self, track: SingingTrack) -> VoiceVoxTrack:
        return VoiceVoxTrack(
            name=track.title,
            solo=track.solo,
            mute=track.mute,
            gain=track.volume,
            notes=[self.generate_note(note) for note in track.note_list],
        )

    def generate_note(self, note: Note) -> VoiceVoxNote:
        if not is_kana(note.lyric):
            lyric = DEFAULT_JAPANESE_LYRIC
            msg_prefix = _("Unsupported lyric: ")
            show_warning(f"{msg_prefix} {note.lyric}")
        else:
            lyric = note.lyric
        return VoiceVoxNote(
            lyric=lyric,
            position=note.start_pos,
            duration=note.length,
            note_number=note.key_number,
        )
