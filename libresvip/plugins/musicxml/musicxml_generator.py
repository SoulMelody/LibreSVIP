import dataclasses
import operator
import re
from collections import defaultdict
from decimal import Decimal
from typing import Optional, cast

from libresvip.core.constants import TICKS_IN_BEAT
from libresvip.model.base import Project, SingingTrack, TimeSignature
from libresvip.utils.music_math import midi2note

from .model import KeyTick, MXmlMeasure, MXmlMeasureContent
from .models.enums import NoteTypeValue, StartStop, Step, Syllabic, TiedType
from .models.mxml4 import (
    Attributes,
    Direction,
    DirectionType,
    Lyric,
    Metronome,
    Notations,
    PerMinute,
    Pitch,
    Rest,
    ScorePart,
    ScorePartwise,
    Sound,
    TextElementData,
    Tie,
    Tied,
    Time,
)
from .models.mxml4 import Note as MusicXMLNote
from .options import OutputOptions

DEFAULT_TICK_RATE_CEVIO = 2.0


@dataclasses.dataclass
class MusicXMLGenerator:
    options: OutputOptions

    def generate_project(self, project: Project) -> ScorePartwise:
        project_with_tick_rate_applied = self.apply_tick_rate(project)
        measures: dict[int, list[MXmlMeasure]] = defaultdict(list)
        for i, track in enumerate(project_with_tick_rate_applied.track_list):
            if key_ticks := self.get_key_ticks(i, track, project_with_tick_rate_applied):
                track_measures = self.get_measures(
                    key_ticks,
                    project_with_tick_rate_applied.time_signature_list,
                    i,
                )
                measures[i].extend(track_measures)
        musicxml_project = ScorePartwise()
        for track_index, measures_part in measures.items():
            track_title = project_with_tick_rate_applied.track_list[track_index].title
            part_node, score_part_node = self.generate_part(measures_part, track_index, track_title)
            musicxml_project.part.append(part_node)
            musicxml_project.part_list.score_part.append(score_part_node)
        return musicxml_project

    def generate_part(
        self,
        measures: list[MXmlMeasure],
        track_index: int,
        track_title: Optional[str],
    ) -> tuple[ScorePartwise.Part, ScorePart]:
        part_id = f"P{track_index + 1}"
        part_node = ScorePartwise.Part(id=part_id)
        score_part = ScorePart(id=part_id)
        if score_part.part_name is not None:
            if track_title:
                score_part.part_name.value = track_title
            else:
                score_part.part_name.value = f"Track {track_index + 1}"
        for i, measure in enumerate(measures):
            measure_node = ScorePartwise.Part.Measure(
                number=str(i + 1),
                attributes=[
                    Attributes(
                        divisions=Decimal.from_float(TICKS_IN_BEAT * DEFAULT_TICK_RATE_CEVIO)
                    )
                ],
            )
            if measure.time_signature is not None:
                measure_node.attributes.append(
                    Attributes(
                        time=[
                            Time(
                                beats=[str(measure.time_signature.numerator)],
                                beat_type=[str(measure.time_signature.denominator)],
                            )
                        ]
                    )
                )
            if measure.contents is not None:
                for content in measure.contents:
                    if content.bpm is not None:
                        sound_node, direction_node = self.generate_nodes_for_tempo(content)
                        measure_node.sound.append(sound_node)
                        measure_node.direction.append(direction_node)
                    elif content.note_type is not None and content.note is not None:
                        if note := self.generate_note_node(content):
                            note.voice = str(track_index + 2)
                            measure_node.note.append(note)
                    else:
                        measure_node.note.append(self.generate_rest_node(content))
            part_node.measure.append(measure_node)
        return part_node, score_part

    def generate_nodes_for_tempo(self, tempo: MXmlMeasureContent) -> tuple[Sound, Direction]:
        sound_node = Sound(tempo=Decimal.from_float(cast(float, tempo.bpm)))
        direction_node = Direction(
            direction_type=[
                DirectionType(
                    metronome=Metronome(
                        beat_unit=[NoteTypeValue.QUARTER],
                        per_minute=PerMinute(value=str(tempo.bpm)),
                    )
                )
            ]
        )
        return sound_node, direction_node

    def generate_rest_node(self, rest: MXmlMeasureContent) -> MusicXMLNote:
        return MusicXMLNote(rest=[Rest()], duration=[Decimal(rest.duration)])

    def generate_note_node(self, note: MXmlMeasureContent) -> Optional[MusicXMLNote]:
        if note.note is None or note.note_type is None:
            return None
        note_node = MusicXMLNote(
            duration=[Decimal(note.duration)],
        )
        key_str = midi2note(note.note.key_number)
        if (octave_matcher := re.search(r"\d+$", key_str)) is not None:
            octave = int(octave_matcher.group())
        else:
            return None
        if (step_matcher := re.search(r"^[A-G]", key_str)) is not None:
            step = Step(step_matcher.group())
        else:
            return None
        alter = 1 if "#" in key_str else 0
        note_node.pitch.append(
            Pitch(
                step=step,
                alter=Decimal(alter) if alter != 0 else None,
                octave=octave,
            )
        )
        tie_type = {
            MXmlMeasureContent.NoteType.BEGIN: "start",
            MXmlMeasureContent.NoteType.END: "stop",
        }.get(note.note_type)
        if tie_type is not None:
            note_node.tie.append(Tie(type_value=StartStop(tie_type)))
            note_node.notations.append(Notations(tied=[Tied(type_value=TiedType(tie_type))]))
        note_node.lyric.append(
            Lyric(
                syllabic=[getattr(Syllabic, note.note_type.name)],
                text=[TextElementData(value=note.note.lyric)],
            )
        )
        return note_node

    @staticmethod
    def apply_tick_rate(project: Project) -> Project:
        return project.model_copy(
            update={
                "song_tempo_list": [
                    tempo.model_copy(
                        update={"position": int(tempo.position * DEFAULT_TICK_RATE_CEVIO)}
                    )
                    for tempo in project.song_tempo_list
                ],
                "track_list": [
                    track.model_copy(
                        update={
                            "note_list": [
                                note.model_copy(
                                    update={
                                        "start_pos": int(note.start_pos * DEFAULT_TICK_RATE_CEVIO),
                                        "length": int(note.length * DEFAULT_TICK_RATE_CEVIO),
                                    }
                                )
                                for note in track.note_list
                            ]
                        }
                    )
                    for track in project.track_list
                    if isinstance(track, SingingTrack)
                ],
            }
        )

    @staticmethod
    def get_key_ticks(track_index: int, track: SingingTrack, project: Project) -> list[KeyTick]:
        tempos = []
        if track_index == 0:
            tempos = [
                KeyTick(tick=tempo.position, tempo=tempo) for tempo in project.song_tempo_list
            ]
        note_starts = [KeyTick(tick=note.start_pos, note_start=note) for note in track.note_list]
        note_ends = [KeyTick(tick=note.end_pos, note_end=note) for note in track.note_list]
        return sorted(note_ends + tempos + note_starts, key=operator.attrgetter("tick"))

    @staticmethod
    def get_measures(
        key_ticks: list[KeyTick],
        time_signatures: list[TimeSignature],
        track_index: int,
    ) -> list[MXmlMeasure]:
        ticks_in_beat = round(TICKS_IN_BEAT * DEFAULT_TICK_RATE_CEVIO)
        measure_border_ticks = [0]
        measure = 0.0
        tick = 0.0
        prev_time_signature = TimeSignature()
        for time_signature in time_signatures:
            previous_measure = int(measure)
            ticks_in_measure = round(prev_time_signature.bar_length(ticks_in_beat))
            tick += ticks_in_measure * (time_signature.bar_index - measure)
            measure = time_signature.bar_index
            current_measure = int(measure)
            measure_border_ticks.extend(
                measure_border_ticks[-1] + ticks_in_measure
                for _ in range(current_measure - previous_measure)
            )
            prev_time_signature = time_signature
        last_tick = key_ticks[-1].tick
        if last_tick >= tick + (
            ticks_in_measure := round(prev_time_signature.bar_length(ticks_in_beat))
        ):
            previous_measure = int(measure)
            tick_diff = last_tick - tick
            measure += tick_diff / ticks_in_measure
            tick = last_tick
            current_measure = int(measure)
            measure_border_ticks.extend(
                measure_border_ticks[-1] + ticks_in_measure
                for _ in range(current_measure - previous_measure)
            )
        measure_border_ticks.append(
            measure_border_ticks[-1] + round(prev_time_signature.bar_length(ticks_in_beat))
        )

        key_ticks_with_measure_borders = [
            (
                border_pair,
                [
                    key_tick
                    for key_tick in key_ticks
                    if (
                        (border_pair[0] < key_tick.tick <= border_pair[1])
                        if key_tick.note_end is not None
                        else (border_pair[0] <= key_tick.tick < border_pair[1])
                    )
                ],
            )
            for border_pair in zip(measure_border_ticks, measure_border_ticks[1:])
        ]

        current_content_group: list[MXmlMeasureContent] = []
        content_group_border_pair_map = {}
        ongoing_note_with_current_head = None
        for border_pair, key_tick_group in key_ticks_with_measure_borders:
            current_tick_in_measure = 0
            current_content_group.clear()
            for key_tick in key_tick_group:
                key_tick_relative = key_tick.tick - border_pair[0]
                if key_tick_relative > current_tick_in_measure:
                    if ongoing_note_with_current_head is None:
                        current_content_group.append(
                            MXmlMeasureContent.with_rest(
                                duration=key_tick_relative - current_tick_in_measure
                            )
                        )
                    current_tick_in_measure = key_tick_relative
                if key_tick.tempo is not None:
                    if ongoing_note_with_current_head is not None:
                        note, head = ongoing_note_with_current_head
                        current_content_group.append(
                            MXmlMeasureContent.note(
                                duration=key_tick.tick - head,
                                note=note,
                                note_type=MXmlMeasureContent.NoteType.BEGIN
                                if note.start_pos == head
                                else MXmlMeasureContent.NoteType.MIDDLE,
                            )
                        )
                        ongoing_note_with_current_head = note, key_tick.tick
                    current_content_group.append(
                        MXmlMeasureContent.with_tempo(bpm=key_tick.tempo.bpm)
                    )
                elif key_tick.note_start is not None:
                    ongoing_note_with_current_head = (
                        key_tick.note_start,
                        key_tick.tick,
                    )
                elif key_tick.note_end is not None and ongoing_note_with_current_head is not None:
                    note, head = ongoing_note_with_current_head
                    current_content_group.append(
                        MXmlMeasureContent.with_note(
                            duration=key_tick.note_end.end_pos - head,
                            note=key_tick.note_end,
                            note_type=MXmlMeasureContent.NoteType.SINGLE
                            if note.start_pos == head
                            else MXmlMeasureContent.NoteType.END,
                        )
                    )
                    ongoing_note_with_current_head = None
            rest_length = border_pair[1] - border_pair[0] - current_tick_in_measure
            if rest_length > 0:
                ongoing_note_at_measure_end = ongoing_note_with_current_head
                if ongoing_note_at_measure_end is None:
                    current_content_group.append(MXmlMeasureContent.with_rest(duration=rest_length))
                else:
                    note, head = ongoing_note_at_measure_end
                    current_content_group.append(
                        MXmlMeasureContent.with_note(
                            duration=border_pair[1] - head,
                            note=note,
                            note_type=MXmlMeasureContent.NoteType.BEGIN
                            if note.start_pos == head
                            else MXmlMeasureContent.NoteType.MIDDLE,
                        )
                    )
                    ongoing_note_with_current_head = note, border_pair[1]
            content_group_border_pair_map[border_pair] = current_content_group.copy()

        return [
            MXmlMeasure(
                tick_start=border_pair[0],
                length=border_pair[1] - border_pair[0],
                time_signature=next(
                    (ts for ts in time_signatures if ts.bar_index == index),
                    None,
                ),
                contents=contents,
            )
            for index, (border_pair, contents) in enumerate(
                sorted(
                    content_group_border_pair_map.items(),
                    key=lambda x: x[0][0],
                )
            )
        ]
