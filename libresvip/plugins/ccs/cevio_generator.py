import dataclasses
import datetime
import uuid
from typing import Optional

from wanakana import PROLONGED_SOUND_MARK
from xsdata.models.datatype import XmlTime

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
    Track,
)
from libresvip.utils.audio import audio_track_info
from libresvip.utils.translation import gettext_lazy as _

from .cevio_pitch import generate_for_cevio
from .constants import DEFAULT_PHONEME, OCTAVE_OFFSET, TICK_RATE
from .model import (
    CeVIOBeat,
    CeVIOCreativeStudioProject,
    CeVIOData,
    CeVIOGroup,
    CeVIONote,
    CeVIOParameter,
    CeVIOSong,
    CeVIOSound,
    CeVIOSoundSource,
    CeVIOTempo,
    CeVIOTime,
    CeVIOUnit,
)
from .options import OutputOptions


@dataclasses.dataclass
class CeVIOGenerator:
    options: OutputOptions
    time_synchronizer: TimeSynchronizer = dataclasses.field(init=False)
    first_bar_length: int = dataclasses.field(init=False)

    def generate_project(self, project: Project) -> CeVIOCreativeStudioProject:
        self.time_synchronizer = TimeSynchronizer(project.song_tempo_list)
        ccs_project = CeVIOCreativeStudioProject()
        ccs_project.generation.svss.sound_sources.sound_source.append(
            CeVIOSoundSource(
                name=self.options.default_singer_name,
                version=self.options.default_singer_version,
                sound_source_id=self.options.default_singer_id,
            )
        )
        scene_node = ccs_project.sequence.scene

        self.first_bar_length = int(project.time_signature_list[0].bar_length())

        default_tempos = self.generate_tempos(project.song_tempo_list)
        default_beats = self.generate_time_signatures(project.time_signature_list)

        for new_unit, new_group in self.generate_tracks(
            project.track_list,
            default_tempos,
            default_beats,
            project.song_tempo_list,
        ):
            scene_node.units.unit.append(new_unit)
            scene_node.groups.group.append(new_group)

        return ccs_project

    def generate_tempos(self, tempos: list[SongTempo]) -> CeVIOTempo:
        tempo_node = CeVIOTempo(sound=[CeVIOSound(clock=0, tempo=tempos[0].bpm)])
        for model in tempos[1:]:
            tempo_node.sound.append(
                CeVIOSound(
                    clock=int(model.position * TICK_RATE),
                    tempo=model.bpm,
                )
            )
        return tempo_node

    def generate_time_signatures(self, time_signatures: list[TimeSignature]) -> CeVIOBeat:
        beat = CeVIOBeat(
            time=[
                CeVIOTime(
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
                CeVIOTime(
                    clock=int(tick * TICK_RATE),
                    beats=time_signature.numerator,
                    beat_type=time_signature.denominator,
                )
            )
            prev_time_signature = time_signature
        return beat

    def generate_tracks(
        self,
        tracks: list[Track],
        tempo: CeVIOTempo,
        beat: CeVIOBeat,
        tempo_list: list[SongTempo],
    ) -> list[tuple[CeVIOUnit, CeVIOGroup]]:
        results = []
        for track in tracks:
            if isinstance(track, SingingTrack):
                new_group = CeVIOGroup(
                    group_id=str(uuid.uuid4()),
                    name=track.title,
                    is_muted=track.mute,
                    is_solo=track.solo,
                    cast_id=self.options.default_singer_id,
                )
                new_unit = CeVIOUnit(
                    cast_id=self.options.default_singer_id,
                    group=new_group.group_id,
                    start_time=XmlTime.from_string("00:00:00.000"),
                    song=CeVIOSong(tempo=tempo, beat=beat),
                )
                new_unit.song.score.note = self.generate_notes(track.note_list)
                if len(track.note_list):
                    max_tick = track.note_list[-1].end_pos
                    max_secs = self.time_synchronizer.get_actual_secs_from_ticks(max_tick)
                    new_unit.duration = XmlTime.from_time(
                        datetime.datetime.fromtimestamp(max_secs, tz=datetime.timezone.utc).time()
                    )

                if log_f0 := self.generate_pitch(track.edited_params.pitch, tempo_list):
                    new_unit.song.parameter.log_f0 = log_f0
                results.append((new_unit, new_group))
            elif isinstance(track, InstrumentalTrack):
                if (
                    track_info := audio_track_info(track.audio_file_path, only_wav=True)
                ) is not None:
                    start_secs = self.time_synchronizer.get_actual_secs_from_ticks(track.offset)
                    start_time = XmlTime.from_time(
                        datetime.datetime.fromtimestamp(start_secs, tz=datetime.timezone.utc).time()
                    )
                    end_time = XmlTime.from_time(
                        datetime.datetime.fromtimestamp(
                            track_info.duration / 1000,
                            tz=datetime.timezone.utc,
                        ).time()
                    )
                    new_group = CeVIOGroup(
                        group_id=str(uuid.uuid4()),
                        name=track.title,
                        is_muted=track.mute,
                        is_solo=track.solo,
                        category="OuterAudio",
                    )
                    new_unit = CeVIOUnit(
                        category="OuterAudio",
                        group=new_group.group_id,
                        file_path=track.audio_file_path,
                        start_time=start_time,
                        duration=end_time,
                    )
                    results.append((new_unit, new_group))
        return results

    def generate_notes(self, notes: list[Note]) -> list[CeVIONote]:
        cevio_notes = []
        for note in notes:
            lyric = chr(PROLONGED_SOUND_MARK) if note.lyric == "-" else note.lyric
            phonetic = None
            if not is_kana(lyric) and not is_romaji(lyric):
                phonetic = DEFAULT_PHONEME
                msg_prefix = _("Unsupported lyric: ")
                show_warning(f"{msg_prefix} {lyric}")
            cevio_notes.append(
                CeVIONote(
                    clock=int(note.start_pos * TICK_RATE),
                    duration=int(note.length * TICK_RATE),
                    lyric=lyric,
                    phonetic=phonetic,
                    pitch_octave=note.key_number // KEY_IN_OCTAVE + OCTAVE_OFFSET,
                    pitch_step=note.key_number % KEY_IN_OCTAVE,
                )
            )
        return cevio_notes

    def generate_pitch(
        self, pitch: ParamCurve, tempo_list: list[SongTempo]
    ) -> Optional[CeVIOParameter]:
        if (data := generate_for_cevio(pitch, tempo_list, self.first_bar_length)) is not None:
            log_f0_node = CeVIOParameter(length=data.length)
            log_f0_node.data.extend(
                CeVIOData(
                    index=each.idx,
                    repeat=each.repeat,
                    value=each.value,
                )
                for each in data.events
            )
            return log_f0_node
