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

from .deepvocal_pitch import (
    DvNoteWithPitch,
    DvSegmentPitchRawData,
    convert_note_key,
    pitch_from_dv_track,
)
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
    first_bar_length: int = dataclasses.field(init=False)

    def parse_project(self, dv_project: DvProject) -> Project:
        time_signatures = self.parse_time_signatures(dv_project.inner_project.time_signatures)
        self.first_bar_length = round(time_signatures[0].bar_length())
        self.tick_prefix = round(time_signatures[0].bar_length() * 4)
        tempos = self.parse_tempos(dv_project.inner_project.tempos)
        instrumental_tracks = self.parse_instrumental_tracks(
            [
                track.track_data
                for track in dv_project.inner_project.tracks
                if track.track_type == DvTrackType.AUDIO and len(track.track_data.infos) > 0
            ]
        )
        singing_tracks = self.parse_singing_tracks(
            [
                track.track_data
                for track in dv_project.inner_project.tracks
                if track.track_type == DvTrackType.SINGING
            ],
            tempos,
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
            time_signature if i > 0 else time_signature.model_copy(update={"bar_index": 0})
            for i, time_signature in enumerate(
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
            )
            if not i or time_signature.bar_index >= 0
        ]

    def parse_tempos(self, dv_tempos: list[DvTempo]) -> list[SongTempo]:
        return [
            song_tempo if i > 0 else song_tempo.model_copy(update={"position": 0})
            for i, song_tempo in enumerate(
                shift_tempo_list(
                    [
                        SongTempo(
                            position=tempo.position,
                            bpm=tempo.bpm / 100,
                        )
                        for tempo in dv_tempos
                    ],
                    -self.tick_prefix,
                )
            )
            if not i or song_tempo.position >= 0
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
        tempo_list: list[SongTempo],
    ) -> list[SingingTrack]:
        track_list = []
        for dv_track in dv_singing_tracks:
            for i, segment in enumerate(dv_track.segments):
                segment_pitch_data = []
                note_with_pitch = []
                tick_offset = segment.start
                track = SingingTrack(
                    title=f"{dv_track.name} {i + 1}",
                    mute=dv_track.mute,
                    solo=dv_track.solo,
                    ai_singer_name=segment.singer_name,
                    note_list=self.parse_notes(
                        segment.notes, note_with_pitch, tick_offset - self.tick_prefix
                    ),
                )
                segment_pitch_data = [
                    DvSegmentPitchRawData(segment.start - self.tick_prefix, segment.pitch_data)
                ]
                if (
                    pitch := pitch_from_dv_track(
                        self.first_bar_length,
                        segment_pitch_data,
                        note_with_pitch,
                        tempo_list,
                    )
                ) is not None:
                    track.edited_params.pitch = pitch
                track_list.append(track)
        return track_list

    def parse_notes(
        self,
        dv_notes: list[DvNote],
        note_with_pitch: list[DvNoteWithPitch],
        tick_offset: int,
    ) -> list[Note]:
        note_list = []
        for dv_note in dv_notes:
            note = Note(
                start_pos=tick_offset + dv_note.start,
                length=dv_note.length,
                key_number=convert_note_key(dv_note.key),
                lyric=dv_note.word,
                pronunciation=dv_note.phoneme,
            )
            note_with_pitch.append(
                DvNoteWithPitch(
                    note=note,
                    ben_dep=dv_note.ben_depth,
                    ben_len=dv_note.ben_length,
                    por_head=dv_note.por_head,
                    por_tail=dv_note.por_tail,
                    vibrato=dv_note.note_vibrato_data.vibrato_points,
                )
            )
            note_list.append(note)
        return note_list
