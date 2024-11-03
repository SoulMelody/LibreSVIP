import dataclasses

from libresvip.model.base import (
    InstrumentalTrack,
    Note,
    ParamCurve,
    Points,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
    Track,
)
from libresvip.model.point import Point

from .model import (
    AISAudioTrack,
    AISNote,
    AISProjectBody,
    AISProjectHead,
    AISSingVoiceTrack,
    AISTempo,
    AISTimeSignature,
    AISTrack,
)
from .options import InputOptions


@dataclasses.dataclass
class AiSingersParser:
    options: InputOptions
    first_bar_length: int = dataclasses.field(init=False)

    def parse_project(self, ais_head: AISProjectHead, ais_body: AISProjectBody) -> Project:
        time_signatures = self.parse_time_signatures(ais_head.signature)
        self.first_bar_length = round(time_signatures[0].bar_length())
        tempos = self.parse_tempos(ais_head.tempo)
        track_list = self.parse_tracks(ais_body.tracks)
        return Project(
            time_signature_list=time_signatures,
            song_tempo_list=tempos,
            track_list=track_list,
        )

    def parse_time_signatures(
        self, ais_time_signatures: list[AISTimeSignature]
    ) -> list[TimeSignature]:
        return [
            TimeSignature(
                numerator=ais_time_signature.beat_zi,
                denominator=ais_time_signature.beat_mu,
                bar_index=ais_time_signature.start_bar,
            )
            for ais_time_signature in ais_time_signatures
        ]

    def parse_tempos(self, ais_tempos: list[AISTempo]) -> list[SongTempo]:
        return [
            SongTempo(
                bpm=ais_tempo.tempo_float,
                position=ais_tempo.start_128 * 15,
            )
            for ais_tempo in ais_tempos
        ]

    def parse_tracks(self, ais_tracks: list[AISTrack]) -> list[Track]:
        track_list = []
        for ais_track in ais_tracks:
            if isinstance(ais_track, AISSingVoiceTrack):
                note_list = []
                pitch_points = [Point.start_point()]
                for item in ais_track.items:
                    tick_prefix = item.start * 15
                    item_notes, pitch_points = self.parse_notes(item.notes, tick_prefix)
                    note_list.extend(item_notes)
                    pitch_points.extend(pitch_points)
                pitch_points.append(Point.end_point())
                singing_track = SingingTrack(
                    title=ais_track.name,
                    ai_singer_name=ais_track.singer_namecn,
                    mute=ais_track.mute,
                    solo=ais_track.solo,
                    note_list=note_list,
                )
                if len(pitch_points) > 2:
                    singing_track.edited_params.pitch = ParamCurve(points=Points(root=pitch_points))
                track_list.append(singing_track)
            elif self.options.import_instrumental_track and isinstance(ais_track, AISAudioTrack):
                track_list.extend(
                    InstrumentalTrack(
                        title=f"{ais_track.name} ({i})",
                        mute=ais_track.mute,
                        solo=ais_track.solo,
                        audio_file_path=item.path_audio,
                        offset=item.start * 15,
                    )
                    for i, item in enumerate(ais_track.items)
                )
        return track_list

    def parse_notes(
        self, ais_notes: list[AISNote], tick_prefix: int
    ) -> tuple[list[Note], list[Point]]:
        note_list = []
        pitch_points = []
        for ais_note in ais_notes:
            note = Note(
                start_pos=ais_note.start * 15 + tick_prefix,
                length=ais_note.length * 15,
                key_number=ais_note.midi_no + 12,
                lyric=ais_note.lyric,
                pronunciation=ais_note.pinyin,
            )
            if self.options.import_pitch:
                tick_step = note.length / len(ais_note.pit)
                pitch_points.append(Point(x=note.start_pos + self.first_bar_length, y=-100))
                for i in range(len(ais_note.pit)):
                    tick = note.start_pos + tick_step * i
                    pitch_points.append(
                        Point(
                            x=round(tick) + self.first_bar_length,
                            y=round((note.key_number) * 100 + ais_note.pit[i] * 10),
                        )
                    )
                pitch_points.append(Point(x=note.end_pos + self.first_bar_length, y=-100))
            note_list.append(note)
        return note_list, pitch_points
