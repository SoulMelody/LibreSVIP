from __future__ import annotations

import abc
from functools import partial
from typing import TYPE_CHECKING, Any, Generic, NamedTuple, TypeVar, Union

from more_itertools import pairwise

from libresvip.utils.music_math import (
    cosine_easing_in_interpolation,
    cosine_easing_in_out_interpolation,
    cosine_easing_out_interpolation,
    linear_interpolation,
)

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable


PointType = TypeVar("PointType")


class Point(NamedTuple):
    x: int
    y: int

    @classmethod
    def start_point(cls, value: int = -100) -> Point:
        return cls(-192000, value)

    @classmethod
    def end_point(cls, value: int = -100) -> Point:
        return cls(1073741823, value)


def _inner_interpolate(
    data: list[Point],
    sampling_interval_tick: int,
    mapping: Callable[[int, Point, Point], float],
) -> list[Point]:
    return (
        (
            [data[0]]
            + [
                Point(x=x, y=round(mapping(x, start, end)))
                for start, end in pairwise(data)
                for x in range(start.x + 1, end.x, sampling_interval_tick)
            ]
            + [data[-1]]
        )
        if data
        else data
    )


interpolate_linear = partial(_inner_interpolate, mapping=linear_interpolation)
interpolate_cosine_ease_in_out = partial(
    _inner_interpolate, mapping=cosine_easing_in_out_interpolation
)
interpolate_cosine_ease_in = partial(_inner_interpolate, mapping=cosine_easing_in_interpolation)
interpolate_cosine_ease_out = partial(_inner_interpolate, mapping=cosine_easing_out_interpolation)


class PointList(abc.ABC, Generic[PointType]):
    root: list[PointType]

    def __len__(self) -> int:
        return len(self.root)

    def __getitem__(self, index: int) -> PointType:
        return self.root[index]

    def __setitem__(self, index: int, value: PointType) -> None:
        self.root[index] = value

    def __delitem__(self, index: int) -> None:
        del self.root[index]

    def __contains__(self, item: PointType) -> bool:
        return item in self.root

    def append(self, item: PointType) -> None:
        self.root.append(item)

    def insert(self, i: int, item: PointType) -> None:
        self.root.insert(i, item)

    def pop(self, i: int = -1) -> PointType:
        return self.root.pop(i)

    def remove(self, item: PointType) -> None:
        self.root.remove(item)

    def clear(self) -> None:
        self.root.clear()

    def count(self, item: PointType) -> int:
        return self.root.count(item)

    def index(self, item: PointType, *args: Any) -> int:
        return self.root.index(item, *args)

    def reverse(self) -> None:
        self.root.reverse()

    def sort(self, /, *args: Any, **kwds: Any) -> None:
        self.root.sort(*args, **kwds)

    def extend(self, other: Union[PointList[PointType], Iterable[PointType]]) -> None:
        if isinstance(other, PointList):
            self.root.extend(other.root)
        else:
            self.root.extend(other)
