import dataclasses
from typing import List

from libresvip.core.constants import DEFAULT_BPM
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import (
    Note,
    ParamCurve,
    Params,
    Point,
    Points,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
)

from .model import DsItem, DsProject
from .options import InputOptions
from .phoneme_dict import get_opencpop_dict
from .utils import hz2midi, note2midi


@dataclasses.dataclass
class DiffSingerParser:
    options: InputOptions
    synchronizer: TimeSynchronizer = dataclasses.field(init=False)

    def parse_project(self, ds_project: DsProject) -> Project:
        sont_tempo_list = [SongTempo(Position=0, BPM=DEFAULT_BPM)]
        self.synchronizer = TimeSynchronizer(sont_tempo_list)
        return Project(
            SongTempoList=sont_tempo_list,
            TimeSignatureList=[TimeSignature(BarIndex=0, Numerator=4, Denominator=4)],
            TrackList=[
                SingingTrack(
                    NoteList=self.parse_notes(ds_project.__root__),
                    EditedParams=Params(Pitch=self.parse_pitch(ds_project.__root__)),
                )
            ],
        )

    def parse_notes(self, ds_items: List[DsItem]) -> List[Note]:
        opencpop_dict = get_opencpop_dict(self.options.dict_name)
        all_notes = []
        for ds_item in ds_items:
            notes = []
            lyrics = [word for word in ds_item.text if word not in ["SP", "AP"]]
            cur_time = self.synchronizer.get_actual_ticks_from_secs(ds_item.offset)
            prev_is_breath = False
            phone_complete = True
            for (
                phone,
                phone_dur,
                note,
                is_slur,
            ) in zip(
                ds_item.ph_seq,
                ds_item.ph_dur,
                ds_item.note_seq,
                ds_item.is_slur_seq,
            ):
                phone_dur = self.synchronizer.get_actual_ticks_from_secs(phone_dur)
                if phone == "SP":
                    pass
                elif phone == "AP":
                    prev_is_breath = True
                else:
                    midi_key = note2midi(note)
                    if not is_slur:
                        if not len(notes):
                            notes.append(
                                Note(
                                    StartPos=cur_time,
                                    Length=phone_dur,
                                    KeyNumber=midi_key,
                                    Pronunciation=phone,
                                    HeadTag="V" if prev_is_breath else None,
                                )
                            )
                            prev_is_breath = False
                            phone_complete = False
                        else:
                            phone_str = notes[-1].pronunciation
                            phone_complete = phone_str in opencpop_dict
                            if phone_complete:
                                notes[-1].pronunciation = None
                                lyric = lyrics.pop(0)
                                if lyric != "啊":
                                    notes[-1].lyric = lyric
                                else:
                                    notes[-1].lyric = opencpop_dict[phone_str].replace(
                                        "v", "u"
                                    )
                            if phone_complete or phone_str is None:
                                notes.append(
                                    Note(
                                        StartPos=cur_time,
                                        Length=phone_dur,
                                        KeyNumber=midi_key,
                                        Pronunciation=phone,
                                        HeadTag="V" if prev_is_breath else None,
                                    )
                                )
                                prev_is_breath = False
                                phone_complete = False
                            else:
                                notes[-1].length += phone_dur
                                notes[-1].pronunciation += " " + phone
                    else:
                        phone_str = notes[-1].pronunciation
                        phone_complete = phone_str in opencpop_dict
                        if phone_complete:
                            notes[-1].pronunciation = None
                            lyric = lyrics.pop(0)
                            if lyric != "啊":
                                notes[-1].lyric = lyric
                            else:
                                notes[-1].lyric = opencpop_dict[phone_str].replace(
                                    "v", "u"
                                )
                            notes.append(
                                Note(
                                    StartPos=cur_time,
                                    Length=phone_dur,
                                    KeyNumber=midi_key,
                                    Lyric="-",
                                )
                            )
                cur_time += phone_dur
            if not phone_complete:
                phone_str = notes[-1].pronunciation
                phone_complete = phone_str in opencpop_dict
                if phone_complete:
                    notes[-1].pronunciation = None
                    lyric = lyrics.pop(0)
                    if lyric != "啊":
                        notes[-1].lyric = lyric
                    else:
                        notes[-1].lyric = opencpop_dict[phone_str].replace("v", "u")
            all_notes.extend(notes)
        return all_notes

    def parse_pitch(self, ds_items: List[DsItem]) -> ParamCurve:
        points = Points(__root__=[])
        points.append(Point.start_point())
        for ds_item in ds_items:
            f0_timestep = ds_item.f0_timestep
            points.append(
                Point(
                    self.synchronizer.get_actual_ticks_from_secs(ds_item.offset) + 1920,
                    -100,
                )
            )
            points.extend(
                [
                    Point(
                        self.synchronizer.get_actual_ticks_from_secs(
                            ds_item.offset + f0_timestep * i
                        )
                        + 1920,
                        round(hz2midi(float(f0)) * 100),
                    )
                    for i, f0 in enumerate(ds_item.f0_seq)
                ]
            )
            points.append(
                Point(
                    self.synchronizer.get_actual_ticks_from_secs(
                        ds_item.offset + f0_timestep * (len(ds_item.f0_seq) - 1)
                    )
                    + 1920,
                    -100,
                )
            )
        points.append(Point.end_point())
        return ParamCurve(PointList=points)
