import dataclasses

from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import Note
from libresvip.utils.search import find_last_index

from .pitch_slide import PitchSlide


@dataclasses.dataclass
class PitchSimulator:
    synchronizer: TimeSynchronizer
    note_list: list[Note]
    slide: PitchSlide
    pitch_tags: list[tuple[float, int]] = dataclasses.field(default_factory=list)

    def __post_init__(self) -> None:
        if len(self.note_list) == 0:
            return
        max_slide_time = self.slide.max_inter_time_in_secs
        max_slide_percent = self.slide.max_inter_time_percent

        current_note = self.note_list[0]
        current_head = self.synchronizer.get_actual_secs_from_ticks(current_note.start_pos)
        current_dur = self.synchronizer.get_duration_secs_from_ticks(
            current_note.start_pos, current_note.end_pos
        )
        current_slide = min(current_dur * max_slide_percent, max_slide_time)

        self.pitch_tags.append((current_head, current_note.key_number))
        for i in range(len(self.note_list) - 1):
            next_note = self.note_list[i + 1]
            next_head = self.synchronizer.get_actual_secs_from_ticks(next_note.start_pos)
            next_dur = self.synchronizer.get_duration_secs_from_ticks(
                next_note.start_pos, next_note.end_pos
            )
            next_slide = min(next_dur * max_slide_percent, max_slide_time)
            interval = next_head - current_head - current_dur
            if interval <= 2 * max_slide_time:
                self.pitch_tags.append(
                    (
                        next_head - interval / 2 - current_slide,
                        current_note.key_number,
                    )
                )
                self.pitch_tags.append(
                    (
                        next_head - interval / 2 + next_slide,
                        next_note.key_number,
                    )
                )
            else:
                self.pitch_tags.append(
                    (
                        next_head - interval / 2 - max_slide_time,
                        current_note.key_number,
                    )
                )
                self.pitch_tags.append(
                    (
                        next_head - interval / 2 + max_slide_time,
                        next_note.key_number,
                    )
                )
            current_note = next_note
            current_head = next_head
            current_dur = next_dur
            current_slide = next_slide
        self.pitch_tags.append((current_head + current_dur, current_note.key_number))

    def pitch_at_ticks(self, ticks: int) -> float:
        return self.pitch_at_secs(self.synchronizer.get_actual_ticks_from_ticks(ticks))

    def pitch_at_secs(self, secs: float) -> float:
        index = find_last_index(self.pitch_tags, lambda tag: tag[0] <= secs)
        if index == -1:
            return self.pitch_tags[0][1] * 100
        elif index == len(self.pitch_tags) - 1:
            return self.pitch_tags[-1][1] * 100
        elif self.pitch_tags[index][1] == self.pitch_tags[index + 1][1]:
            return self.pitch_tags[index][1] * 100
        else:
            ratio = self.slide.apply(
                (secs - self.pitch_tags[index][0])
                / (self.pitch_tags[index + 1][0] - self.pitch_tags[index][0])
            )
            return (
                self.pitch_tags[index][1] * (1 - ratio) + self.pitch_tags[index + 1][1] * ratio
            ) * 100
