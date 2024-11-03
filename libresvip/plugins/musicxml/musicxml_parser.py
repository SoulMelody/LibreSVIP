import dataclasses
from typing import Optional

from libresvip.core.constants import DEFAULT_PHONEME, TICKS_IN_BEAT
from libresvip.model.base import (
    Note,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
)
from libresvip.utils.music_math import note2midi

from .models.enums import StartStop
from .models.mxml4 import ScorePart, ScorePartwise
from .options import InputOptions


@dataclasses.dataclass
class MusicXMLParser:
    options: InputOptions

    def parse_project(self, mxml: ScorePartwise) -> Project:
        part_nodes = mxml.part

        master_track = next((part for part in part_nodes if part.measure), None)
        assert master_track is not None
        (
            time_signatures,
            tempos,
            import_tick_rate,
        ) = self.parse_master_track(master_track)
        time_signatures = time_signatures or [TimeSignature()]
        tempos = tempos or [SongTempo()]

        tracks = []
        for index, part in enumerate(part_nodes):
            score_part = None
            if mxml.part_list is not None and part.id is not None:
                score_part = next(
                    (item for item in mxml.part_list.score_part if item.id == part.id),
                    None,
                )
            tracks.append(self.parse_track(index, part, score_part, import_tick_rate))

        return Project(
            track_list=tracks,
            time_signature_list=time_signatures,
            song_tempo_list=tempos,
        )

    def parse_master_track(
        self, part_node: ScorePartwise.Part
    ) -> tuple[list[TimeSignature], list[SongTempo], float]:
        measure_nodes = part_node.measure
        assert measure_nodes[0].attributes[0].divisions is not None
        divisions = int(measure_nodes[0].attributes[0].divisions)
        import_tick_rate = TICKS_IN_BEAT / divisions
        tempos = []
        time_signatures = []
        tick_position = 0
        current_time_signature = TimeSignature()
        for i, measure_node in enumerate(measure_nodes):
            if (
                len(measure_node.attributes)
                and len(measure_node.attributes[0].time)
                and (time_signature_node := measure_node.attributes[0].time[0])
            ):
                bar_index = int(time_signature_node.number or i)
                numerator = int(time_signature_node.beats[0])
                denominator = int(time_signature_node.beat_type[0])
                current_time_signature = TimeSignature(
                    bar_index=bar_index, numerator=numerator, denominator=denominator
                )
                time_signatures.append(current_time_signature)

            sound_nodes = measure_node.sound
            if len(sound_nodes) and (sound_node := sound_nodes[0]).tempo:
                tempo = SongTempo(
                    position=tick_position,
                    bpm=float(sound_node.tempo),
                )
                tempos.append(tempo)

            tick_position += round(current_time_signature.bar_length())
        return time_signatures, tempos, import_tick_rate

    def parse_track(
        self,
        track_index: int,
        part_node: ScorePartwise.Part,
        score_part: Optional[ScorePart],
        import_tick_rate: float,
    ) -> SingingTrack:
        track_name = (
            score_part.part_name.value
            if score_part is not None and score_part.part_name is not None
            else f"Track {track_index + 1}"
        )
        notes = []
        is_inside_note = False
        measure_nodes = part_node.measure
        tick_position = 0
        for measure_node in measure_nodes:
            note_nodes = measure_node.note
            for note_node in note_nodes:
                duration_nodes = note_node.duration
                duration = (
                    int(float(duration_nodes[0]) * import_tick_rate)
                    if len(duration_nodes)
                    else None
                )
                if not duration:
                    if note_node.grace:
                        continue
                    else:
                        msg = "Duration not found"
                        raise ValueError(msg)

                rest_nodes = note_node.rest
                if rest_nodes:
                    tick_position += duration
                    continue

                pitch_node = note_node.pitch[0]
                step = pitch_node.step
                assert step is not None
                assert pitch_node.octave is not None
                alter_node = pitch_node.alter
                alter = int(alter_node) if alter_node else 0
                octave = int(pitch_node.octave)
                key = note2midi(f"{step.value}{octave}") + alter

                lyric_nodes = note_node.lyric
                lyric = (
                    lyric_nodes[0].text[0].value
                    if len(lyric_nodes) and len(lyric_nodes[0].text)
                    else DEFAULT_PHONEME
                )

                if not is_inside_note:
                    note = Note(
                        key_number=key,
                        lyric=lyric,
                        start_pos=tick_position,
                        length=duration,
                    )
                    notes.append(note)
                else:
                    notes[-1] = notes[-1].model_copy(
                        update={
                            "length": notes[-1].length + duration,
                        }
                    )

                tick_position += duration

                tie_nodes = note_node.tie
                if len(tie_nodes) and (tie_node := tie_nodes[0]) and tie_node.type_value:
                    if tie_node.type_value == StartStop.START:
                        is_inside_note = True
                    elif tie_node.type_value == StartStop.STOP:
                        is_inside_note = False

        return SingingTrack(
            title=track_name,
            note_list=notes,
        )
