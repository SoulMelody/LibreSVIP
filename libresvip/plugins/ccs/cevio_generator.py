import dataclasses
import datetime
import itertools
import math
import operator
import uuid
from typing import Optional

from xsdata.models.datatype import XmlTime

from libresvip.core.constants import KEY_IN_OCTAVE
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import (
    Note,
    ParamCurve,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
    Track,
)

from .cevio_pitch import generate_for_cevio
from .constants import FIXED_MEASURE_PREFIX, OCTAVE_OFFSET, TICK_RATE
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

        measure_prefix = FIXED_MEASURE_PREFIX
        tick_prefix = project.time_signature_list[0].bar_index * TICK_RATE * measure_prefix

        default_tempos = self.generate_tempos(project.song_tempo_list, tick_prefix)
        default_beats = self.generate_time_signatures(project.time_signature_list, tick_prefix)

        for new_unit, new_group in self.generate_tracks(project.track_list, default_tempos, default_beats, tick_prefix):
            scene_node.units.unit.append(new_unit)
            scene_node.groups.group.append(new_group)

        return ccs_project

    def generate_tempos(self, tempos: list[SongTempo], tick_prefix: int) -> CeVIOTempo:
        tempo_node = CeVIOTempo(
            sound=[CeVIOSound(clock=0, tempo=tempos[0].bpm)]
        )
        for model in tempos[1:]:
            tempo_node.sound.append(CeVIOSound(
                clock=int(model.position * TICK_RATE + tick_prefix),
                tempo=model.bpm,
            ))
        return tempo_node

    def generate_time_signatures(self, time_signatures: list[TimeSignature], tick_prefix: int) -> CeVIOBeat:
        beat = CeVIOBeat(
            time=[CeVIOTime(
                clock=0,
                beats=time_signatures[0].numerator,
                beat_type=time_signatures[0].denominator,
            )]
        )
        tick = 0.0
        prev_time_signature = time_signatures[0]
        for time_signature in time_signatures[1:]:
            if time_signature.bar_index > prev_time_signature.bar_index:
                tick += (time_signature.bar_index - prev_time_signature.bar_index) * prev_time_signature.bar_length()
            beat.time.append(CeVIOTime(
                clock=int(tick * TICK_RATE) + tick_prefix,
                beats=time_signature.numerator,
                beat_type=time_signature.denominator,
            ))
            prev_time_signature = time_signature
        return beat

    def generate_tracks(self, tracks: list[Track], tempo: CeVIOTempo, beat: CeVIOBeat, tick_prefix: int) -> list[tuple[CeVIOUnit, CeVIOGroup]]:
        results = []
        for track in tracks:
            if isinstance(track, SingingTrack):
                new_group = CeVIOGroup(
                    group_id=str(uuid.uuid4()),
                    name=track.title,
                    is_muted=track.mute,
                    is_solo=track.solo,
                    cast_id=self.options.default_singer_id
                )
                new_unit = CeVIOUnit(
                    cast_id=self.options.default_singer_id, group=new_group.group_id,
                    start_time=XmlTime.from_string("00:00:00.000"),
                    song=CeVIOSong(
                        tempo=tempo, beat=beat
                    )
                )
                new_unit.song.score.note = self.generate_notes(track.note_list, tick_prefix)
                if len(track.note_list):
                    max_tick = track.note_list[-1].end_pos
                    max_secs = self.time_synchronizer.get_actual_secs_from_ticks(max_tick)
                    new_unit.duration = XmlTime.from_time(datetime.time(second=math.ceil(max_secs)))

                # if log_f0 := self.generate_pitch(track.edited_params.pitch, tick_prefix):
                #     new_unit.song.parameter.log_f0 = log_f0
                results.append((new_unit, new_group))
        return results

    def generate_notes(self, notes: list[Note], tick_prefix: int) -> list[CeVIONote]:
        ccs_notes = []
        for note in notes:
            ccs_notes.append(CeVIONote(
                clock=int(note.start_pos * TICK_RATE + tick_prefix),
                duration=int(note.length * TICK_RATE),
                lyric=note.lyric,
                pitch_octave=note.key_number // KEY_IN_OCTAVE + OCTAVE_OFFSET,
                pitch_step=note.key_number % KEY_IN_OCTAVE,
            ))
        return ccs_notes

    def generate_pitch(self, pitch: ParamCurve, tick_prefix: int) -> Optional[CeVIOParameter]:
        if (events := generate_for_cevio(pitch, tick_prefix)) is not None:
            log_f0_node = CeVIOParameter(length=len(events))
            for index, group in itertools.groupby(events, operator.attrgetter("index")):
                group = list(group)
                log_f0_node.data.append(CeVIOData(
                    index=index,
                    repeat=len(group) if len(group) > 1 else None,
                    value=group[0].value,
                ))
            return log_f0_node
