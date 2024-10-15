import dataclasses
from typing import cast

import more_itertools

from libresvip.core.constants import DEFAULT_BPM
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import (
    Note,
    ParamCurve,
    Params,
    Points,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
)
from libresvip.model.point import Point
from libresvip.utils.music_math import hz2midi, note2midi

from .model import DsItem, DsProject
from .options import InputOptions


@dataclasses.dataclass
class DiffSingerParser:
    options: InputOptions
    synchronizer: TimeSynchronizer = dataclasses.field(init=False)

    def parse_project(self, ds_project: DsProject) -> Project:
        sont_tempo_list = [SongTempo(position=0, bpm=DEFAULT_BPM)]
        self.synchronizer = TimeSynchronizer(sont_tempo_list)
        return Project(
            song_tempo_list=sont_tempo_list,
            time_signature_list=[TimeSignature(bar_index=0, numerator=4, denominator=4)],
            track_list=[
                SingingTrack(
                    note_list=self.parse_notes(ds_project.root),
                    edited_params=Params(pitch=self.parse_pitch(ds_project.root)),
                )
            ],
        )

    def parse_notes(self, ds_items: list[DsItem]) -> list[Note]:
        all_notes = []
        for ds_item in ds_items:
            notes: list[Note] = []
            cur_time = self.synchronizer.get_actual_ticks_from_secs(float(ds_item.offset))
            prev_is_breath = False
            for lyric_index, slur_group in enumerate(
                more_itertools.split_before(
                    enumerate(ds_item.note_slur or []),
                    lambda pair: pair[1] == 0,
                )
            ):
                if not ds_item.note_dur:
                    break
                for note_index, is_slur in slur_group:
                    text = ds_item.text[lyric_index]
                    note_dur = ds_item.note_dur[note_index]
                    note = ds_item.note_seq[note_index]
                    note_dur = self.synchronizer.get_actual_ticks_from_secs(note_dur)
                    if text == "SP":
                        pass
                    elif text == "AP":
                        prev_is_breath = True
                    else:
                        midi_key = note2midi(note)
                        if not is_slur:
                            notes.append(
                                Note(
                                    start_pos=int(cur_time),
                                    length=int(note_dur),
                                    key_number=midi_key,
                                    lyric=text,
                                    head_tag="V" if prev_is_breath else None,
                                )
                            )
                            prev_is_breath = False
                        else:
                            notes.append(
                                Note(
                                    start_pos=int(cur_time),
                                    length=int(note_dur),
                                    key_number=midi_key,
                                    lyric="-",
                                )
                            )
                    cur_time += note_dur
            all_notes.extend(notes)
        return all_notes

    def parse_pitch(self, ds_items: list[DsItem]) -> ParamCurve:
        points = Points(root=[])
        points.append(Point.start_point())
        if self.options.import_pitch:
            for ds_item in ds_items:
                if ds_item.f0_timestep is None or ds_item.f0_seq is None:
                    continue
                f0_timestep = ds_item.f0_timestep
                points.append(
                    Point(
                        round(self.synchronizer.get_actual_ticks_from_secs(float(ds_item.offset)))
                        + 1920,
                        -100,
                    )
                )
                points.extend(
                    [
                        Point(
                            round(
                                self.synchronizer.get_actual_ticks_from_secs(
                                    cast(float, ds_item.offset) + f0_timestep * i
                                )
                            )
                            + 1920,
                            round(hz2midi(float(f0)) * 100),
                        )
                        for i, f0 in enumerate(cast(list[float], ds_item.f0_seq))
                    ]
                )
                points.append(
                    Point(
                        round(
                            self.synchronizer.get_actual_ticks_from_secs(
                                cast(float, ds_item.offset)
                                + f0_timestep * (len(cast(list[float], ds_item.f0_seq)) - 1)
                            )
                        )
                        + 1920,
                        -100,
                    )
                )
        points.append(Point.end_point())
        return ParamCurve(points=points)
