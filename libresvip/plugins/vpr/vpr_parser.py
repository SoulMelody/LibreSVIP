import dataclasses
import pathlib
import zipfile

from libresvip.core.constants import (
    DEFAULT_CHINESE_LYRIC,
    DEFAULT_ENGLISH_LYRIC,
    DEFAULT_JAPANESE_LYRIC,
    DEFAULT_KOREAN_LYRIC,
)
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

from .constants import (
    BPM_RATE,
    PITCH_BEND_NAME,
    PITCH_BEND_SENSITIVITY_NAME,
)
from .model import (
    VocaloidAudioTrack,
    VocaloidLanguage,
    VocaloidNotes,
    VocaloidPartPitchData,
    VocaloidPoint,
    VocaloidProject,
    VocaloidTimeSig,
    VocaloidTracks,
)
from .options import InputOptions
from .vocaloid_pitch import pitch_from_vocaloid_parts


@dataclasses.dataclass
class VocaloidParser:
    options: InputOptions
    archive_file: zipfile.ZipFile
    first_bar_length: int = dataclasses.field(init=False)
    synchronizer: TimeSynchronizer = dataclasses.field(init=False)
    comp_id2name: dict[str, str] = dataclasses.field(init=False)

    def parse_project(self, vpr_project: VocaloidProject) -> Project:
        self.comp_id2name = {
            voice.comp_id: voice.name
            for voice in vpr_project.voices
            if voice.comp_id is not None and voice.name is not None
        }
        song_tempo_list = self.parse_tempos(vpr_project.master_track.tempo.events)
        self.synchronizer = TimeSynchronizer(song_tempo_list)
        return Project(
            time_signature_list=self.parse_time_signatures(
                vpr_project.master_track.time_sig.events
            ),
            song_tempo_list=song_tempo_list,
            track_list=self.parse_tracks(vpr_project.tracks),
        )

    def parse_time_signatures(
        self, vocaloid_time_signatures: list[VocaloidTimeSig]
    ) -> list[TimeSignature]:
        time_signatures = [
            TimeSignature(
                bar_index=time_signature.bar,
                numerator=time_signature.numer,
                denominator=time_signature.denom,
            )
            for time_signature in vocaloid_time_signatures
        ]
        self.first_bar_length = round(time_signatures[0].bar_length())
        return time_signatures

    def parse_tempos(self, tempos: list[VocaloidPoint]) -> list[SongTempo]:
        return [
            SongTempo(
                position=tempo.pos,
                bpm=tempo.value / BPM_RATE,
            )
            for tempo in tempos
            if tempo.value is not None
        ]

    def parse_tracks(self, tracks: list[VocaloidTracks]) -> list[Track]:
        track_list = []
        for track in tracks:
            if isinstance(track, VocaloidAudioTrack):
                if self.options.import_instrumental_track:
                    for part in track.parts:
                        if part.wav is None:
                            continue
                        if self.options.extract_audio:
                            archive_wav_path = f"Project/Audio/{part.wav.name}"
                            if not (
                                wav_path := pathlib.Path(part.wav.original_name or part.wav.name)
                            ).exists():
                                wav_path.write_bytes(self.archive_file.read(archive_wav_path))
                        instrumental_track = InstrumentalTrack(
                            title=part.name,
                            offset=part.pos,
                            mute=track.is_muted,
                            solo=track.is_solo_mode,
                            audio_file_path=part.wav.original_name or part.wav.name,
                        )
                        track_list.append(instrumental_track)
            else:
                for part in track.parts:
                    comp_id = ""
                    supported_lang_ids = []
                    if part.voice is not None:
                        comp_id = part.voice.comp_id or ""
                        supported_lang_ids.append(part.voice.lang_id)
                    elif part.ai_voice is not None:
                        comp_id = part.ai_voice.comp_id or ""
                        supported_lang_ids.extend(part.ai_voice.lang_ids)
                    if len(supported_lang_ids):
                        main_lang_id = supported_lang_ids[0]
                    else:
                        main_lang_id = VocaloidLanguage.SIMPLIFIED_CHINESE
                    if main_lang_id == VocaloidLanguage.JAPANESE:
                        default_lyric = DEFAULT_JAPANESE_LYRIC
                    elif main_lang_id == VocaloidLanguage.KOREAN:
                        default_lyric = DEFAULT_KOREAN_LYRIC
                    elif main_lang_id == VocaloidLanguage.SIMPLIFIED_CHINESE:
                        default_lyric = DEFAULT_CHINESE_LYRIC
                    else:
                        default_lyric = DEFAULT_ENGLISH_LYRIC
                    singing_track = SingingTrack(
                        title=part.name,
                        mute=track.is_muted,
                        solo=track.is_solo_mode,
                        note_list=self.parse_notes(part.notes, part.pos, default_lyric),
                        ai_singer_name=self.comp_id2name.get(comp_id, ""),
                    )
                    if (
                        self.options.import_pitch
                        and (
                            part_data := VocaloidPartPitchData(
                                start_pos=part.pos,
                                pit=part.get_controller_events(PITCH_BEND_NAME),
                                pbs=part.get_controller_events(PITCH_BEND_SENSITIVITY_NAME),
                            )
                        )
                        and (
                            part_pitch := pitch_from_vocaloid_parts(
                                [part_data],
                                self.synchronizer,
                                singing_track.note_list,
                                self.first_bar_length,
                            )
                        )
                        is not None
                    ):
                        singing_track.edited_params.pitch = part_pitch
                    track_list.append(singing_track)
        return track_list

    def parse_notes(self, notes: list[VocaloidNotes], pos: int, default_lyric: str) -> list[Note]:
        note_list: list[Note] = []
        if len(notes):
            next_pos = None
            for note in notes[::-1]:
                if next_pos is None:
                    normalized_duration = note.duration or 0
                else:
                    normalized_duration = min(note.duration or 0, next_pos - note.pos)
                if normalized_duration > 0:
                    note_list.insert(
                        0,
                        Note(
                            start_pos=note.pos + pos,
                            length=normalized_duration,
                            key_number=note.number,
                            lyric=note.lyric or default_lyric,
                            pronunciation=None,
                        ),
                    )
                next_pos = note.pos
        return note_list
