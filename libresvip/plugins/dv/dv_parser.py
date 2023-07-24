import dataclasses

from libresvip.core.tick_counter import shift_beat_list, shift_tempo_list
from libresvip.model.base import (
    InstrumentalTrack,
    Note,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
)

from .constants import NOTE_KEY_SUM
from .model import (
    DvAudioTrack,
    DvNote,
    DvProject,
    DvSingingTrack,
    DvTempo,
    DvTimeSignature,
    DvTrackType,
)
from .options import InputOptions


@dataclasses.dataclass
class DeepVocalParser:
    options: InputOptions
    tick_prefix: int = dataclasses.field(init=False)

    def parse_project(self, dv_project: DvProject) -> Project:
        time_signatures = self.parse_time_signatures(
            dv_project.inner_project.time_signatures
        )
        self.tick_prefix = round(time_signatures[0].bar_length() * 4)
        tempos = self.parse_tempos(dv_project.inner_project.tempos)
        instrumental_tracks = self.parse_instrumental_tracks(
            [
                track.track_data
                for track in dv_project.inner_project.tracks
                if track.track_type == DvTrackType.AUDIO
                and len(track.track_data.infos) > 0
            ]
        )
        singing_tracks = self.parse_singing_tracks(
            [
                track.track_data
                for track in dv_project.inner_project.tracks
                if track.track_type == DvTrackType.SINGING
            ]
        )
        return Project(
            time_signature_list=time_signatures,
            song_tempo_list=tempos,
            track_list=singing_tracks + instrumental_tracks,
        )

    def parse_time_signatures(
        self, dv_time_signatures: list[DvTimeSignature]
    ) -> list[TimeSignature]:
        return [
            time_signature
            for time_signature in
            shift_beat_list(
                [
                    TimeSignature(
                        bar_index=ts.measure_position,
                        numerator=ts.numerator,
                        denominator=ts.denominator,
                    )
                    for ts in dv_time_signatures
                ],
                -1,
            )
            if time_signature.bar_index >= 0
        ]

    def parse_tempos(self, dv_tempos: list[DvTempo]) -> list[SongTempo]:
        return [
            song_tempo
            for song_tempo in
            shift_tempo_list(
                [
                    SongTempo(
                        position=tempo.position,
                        bpm=tempo.bpm / 100,
                    )
                    for tempo in dv_tempos
                ],
                - self.tick_prefix,
            )
            if song_tempo.position >= 0
        ]

    def parse_instrumental_tracks(
        self, dv_audio_tracks: list[DvAudioTrack]
    ) -> list[InstrumentalTrack]:
        track_list = []
        for dv_track in dv_audio_tracks:
            track = InstrumentalTrack(
                title=dv_track.name or dv_track.infos[0].name,
                mute=dv_track.mute,
                solo=dv_track.solo,
                offset=dv_track.infos[0].start + self.tick_prefix,
                audio_file_path=dv_track.infos[0].path,
            )
            track_list.append(track)
        return track_list

    def parse_singing_tracks(
        self,
        dv_singing_tracks: list[DvSingingTrack],
    ) -> list[SingingTrack]:
        track_list = []
        for dv_track in dv_singing_tracks:
            for i, segment in enumerate(dv_track.segments):
                tick_offset = segment.start
                track = SingingTrack(
                    title=f"{dv_track.name} {i + 1}",
                    mute=dv_track.mute,
                    solo=dv_track.solo,
                    ai_singer_name=segment.singer_name,
                    note_list=self.parse_notes(segment.notes, tick_offset - self.tick_prefix),
                )
                track_list.append(track)
        return track_list

    def parse_notes(self, dv_notes: list[DvNote], tick_offset: int) -> list[Note]:
        note_list = []
        for dv_note in dv_notes:
            note = Note(
                start_pos=tick_offset + dv_note.start,
                length=dv_note.length,
                key_number=int(NOTE_KEY_SUM) - dv_note.key,
                lyric=dv_note.word,
                pronunciation=dv_note.phoneme,
            )
            note_list.append(note)
        return note_list
