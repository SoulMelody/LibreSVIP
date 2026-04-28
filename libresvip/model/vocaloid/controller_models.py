import operator
from dataclasses import dataclass, field

from libresvip.model.point import Point


@dataclass(frozen=True)
class ControllerEvent:
    pos: int
    value: int


@dataclass
class ControllerCurve:
    name: str
    events: list[ControllerEvent] = field(default_factory=list)
    default_value: int = 0
    min_value: int = -127
    max_value: int = 127

    def __post_init__(self) -> None:
        if self.events:
            object.__setattr__(self, "events", sorted(self.events, key=operator.attrgetter("pos")))

    def get_value_at(self, pos: int) -> int:
        current_value = self.default_value
        for event in self.events:
            if event.pos <= pos:
                current_value = event.value
            else:
                break
        return current_value

    def get_value_range(self, start_pos: int, end_pos: int) -> list[tuple[int, int]]:
        result = []

        for event in self.events:
            if event.pos > end_pos:
                break
            if event.pos >= start_pos:
                result.append((event.pos, event.value))

        return result

    def to_points(self, start_pos: int | None = None, end_pos: int | None = None) -> list[Point]:
        points = []

        for i, event in enumerate(self.events):
            if start_pos is not None and event.pos < start_pos:
                continue
            if end_pos is not None and event.pos > end_pos:
                break

            points.append(Point(x=event.pos, y=event.value))

        return points

    def to_interpolated_points(self, step: int = 5) -> list[Point]:
        if not self.events:
            return []

        points = []
        current_value = self.default_value
        prev_pos = None

        for event in self.events:
            if prev_pos is not None and event.pos > prev_pos + step:
                points.append(Point(x=event.pos - 1, y=current_value))

            points.append(Point(x=event.pos, y=event.value))
            current_value = event.value
            prev_pos = event.pos

        return points

    def is_empty(self) -> bool:
        return len(self.events) == 0
