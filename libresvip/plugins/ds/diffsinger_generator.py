from dataclasses import dataclass
from math import ceil

from libresvip.core.exceptions import NoTrackError
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import Project, SingingTrack
from libresvip.utils.translation import gettext_lazy as _

from .model import DsItem
from .models.ds_project import DsProjectModel
from .options import OutputOptions
from .utils import pinyin_util
from .utils.gender_param_utils import GenderParamUtils
from .utils.note_list_util import encode_notes
from .utils.pitch_param_utils import PitchParamUtils


@dataclass
class DiffSingerGenerator:
    options: OutputOptions
    trailing_space: float = 0.05

    def generate(self, project: Project) -> DsItem:
        pinyin_util.load_phoneme_table(self.options.dict_name)
        synchronizer = TimeSynchronizer(project.song_tempo_list)
        if self.options.track_index < 0:
            singing_track = next(
                (track for track in project.track_list if isinstance(track, SingingTrack)),
                None,
            )
        else:
            singing_track = project.track_list[self.options.track_index]
        if singing_track is None:
            msg = _("No singing track found")
            raise NoTrackError(msg)
        os_notes = singing_track.note_list
        ds_project = DsProjectModel()
        ds_project.note_list = encode_notes(os_notes, synchronizer, self.trailing_space)
        total_duration = ceil(sum(note.duration for note in ds_project.note_list) * 1000)
        os_pitch_param_curve = singing_track.edited_params.pitch
        ds_project.pitch_param_curve = PitchParamUtils.encode(os_pitch_param_curve, total_duration)

        if self.options.export_gender:
            os_gender_param_curve = singing_track.edited_params.gender
            ds_project.gender_param_curve = GenderParamUtils.encode(
                os_gender_param_curve, total_duration
            )

        return ds_project.to_param_model()
