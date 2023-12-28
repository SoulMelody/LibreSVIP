from dataclasses import dataclass, field

from ..model import DsItem
from .ds_note import DsNote
from .ds_param_curve import DsParamCurve


@dataclass
class DsProjectModel:
    note_list: list[DsNote] = field(default_factory=list)
    pitch_param_curve: DsParamCurve = field(default_factory=DsParamCurve)
    gender_param_curve: DsParamCurve = field(default_factory=DsParamCurve)

    def to_param_model(self) -> DsItem:
        ds_notes = self.note_list
        input_text = ""
        phoneme_seq = ""
        phoneme_counts = []
        input_note_seq = ""
        input_duration = ""
        input_slur = ""
        input_duration_seq = ""
        is_slur_seq = ""
        phoneme_dur_seq = ""
        for i in range(len(ds_notes)):
            cur_note = ds_notes[i]
            ds_phoneme = cur_note.ds_phoneme
            consonant = ds_phoneme.consonant
            vowel = ds_phoneme.vowel
            input_text += cur_note.lyric.replace("-", "")
            phoneme_counts.append(1)
            if consonant.phoneme:
                phoneme_seq += f"{consonant.phoneme} "
                phoneme_dur_seq += f"{consonant.duration} "
                is_slur_seq += "0 "
                input_duration_seq += f"{consonant.duration} "
                phoneme_counts[-1] += 1
            phoneme_seq += vowel.phoneme
            phoneme_dur_seq += str(vowel.duration)
            input_note_seq += vowel.note_name
            input_duration += str(cur_note.duration)
            input_duration_seq += str(cur_note.duration)
            is_slur_seq += "1" if cur_note.is_slur else "0"
            input_slur += "1" if cur_note.is_slur else "0"
            if i < len(ds_notes) - 1:
                if not cur_note.is_slur:
                    input_text += " "
                input_note_seq += " "
                input_duration += " "
                input_duration_seq += " "
                input_slur += " "
                is_slur_seq += " "
                phoneme_seq += " "
                phoneme_dur_seq += " "

        pitch_points = self.pitch_param_curve.point_list
        f0_sequence = None
        if pitch_points and len(pitch_points) > 0:
            f0_sequence = " ".join(f"{p.value:.1f}" for p in pitch_points)

        gender_points = self.gender_param_curve.point_list
        gender_sequence = None
        if gender_points and len(gender_points) > 0:
            gender_sequence = " ".join(f"{p.value:.1f}" for p in gender_points)

        return DsItem(
            text=input_text,
            ph_seq=phoneme_seq,
            note_seq=input_note_seq,
            note_dur=input_duration,
            note_dur_seq=input_duration_seq,
            note_slur=input_slur,
            is_slur_seq=is_slur_seq,
            ph_dur=phoneme_dur_seq,
            ph_num=" ".join(str(phoneme_count) for phoneme_count in phoneme_counts),
            f0_timestep=str(self.pitch_param_curve.step_size),
            f0_seq=f0_sequence,
            gender_timestep=str(self.gender_param_curve.step_size),
            gender=gender_sequence,
            offset=0,
            input_type="phoneme",
        )
