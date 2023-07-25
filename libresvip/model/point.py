from __future__ import annotations

import math
from functools import partial
from typing import Generic, NamedTuple, TypeVar, Union

from more_itertools import pairwise
from pydantic import (
    BaseModel,
    Field,
    SerializationInfo,
    ValidationInfo,
    model_serializer,
    model_validator,
)

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
    mapping: callable[[Point, Point, int], float],
) -> list[Point]:
    return (
        data
        if not data
        else [data[0]]
        + [
            Point(x=x, y=round(mapping(start, end, x)))
            for start, end in pairwise(data)
            for x in range(start.x + 1, end.x, sampling_interval_tick)
        ]
        + [data[-1]]
    )


def linear_interpolation(
    start: tuple[float, float], end: tuple[float, float], x: int
) -> float:
    x0, y0 = start
    x1, y1 = end
    return y0 + (x - x0) * (y1 - y0) / (x1 - x0)


interpolate_linear = partial(_inner_interpolate, mapping=linear_interpolation)


def cosine_easing_in_out_interpolation(
    start: tuple[float, float], end: tuple[float, float], x: int
) -> float:
    x0, y0 = start
    x1, y1 = end
    return (y0 + y1) / 2 + (y0 - y1) * math.cos((x - x0) / (x1 - x0) * math.pi) / 2


interpolate_cosine_ease_in_out = partial(
    _inner_interpolate, mapping=cosine_easing_in_out_interpolation
)


def cosine_easing_in_interpolation(
    start: tuple[float, float], end: tuple[float, float], x: int
) -> float:
    x0, y0 = start
    x1, y1 = end
    return y1 + (y0 - y1) * math.cos((x - x0) / (x1 - x0) * math.pi / 2)


interpolate_cosine_ease_in = partial(
    _inner_interpolate, mapping=cosine_easing_in_interpolation
)


def cosine_easing_out_interpolation(
    start: tuple[float, float], end: tuple[float, float], x: int
) -> float:
    x0, y0 = start
    x1, y1 = end
    return y0 + (y0 - y1) * math.cos((x - x0) / (x1 - x0) * math.pi / 2 + math.pi / 2)


interpolate_cosine_ease_out = partial(
    _inner_interpolate, mapping=cosine_easing_out_interpolation
)


def sin_easing_in_out_interpolation(
    start: tuple[float, float], end: tuple[float, float], x: float
) -> float:
    x0, y0 = start
    x1, y1 = end
    return y0 + (y1 - y0) * (1 - math.cos((x - x0) / (x1 - x0) * math.pi)) / 2


def sin_easing_in_interpolation(
    start: tuple[float, float], end: tuple[float, float], x: float
) -> float:
    x0, y0 = start
    x1, y1 = end
    return y0 + (y1 - y0) * (1 - math.cos((x - x0) / (x1 - x0) * math.pi / 2))


def sin_easing_out_interpolation(
    start: tuple[float, float], end: tuple[float, float], x: float
) -> float:
    x0, y0 = start
    x1, y1 = end
    return y0 + (y1 - y0) * math.sin((x - x0) / (x1 - x0) * math.pi / 2)


class PointList(BaseModel, Generic[PointType]):
    root: list[PointType] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def populate_root(cls, values, _info: ValidationInfo):
        return {"root": values} if isinstance(values, list) else values

    @model_serializer(mode="wrap")
    def _serialize(self, handler: callable, info: SerializationInfo):
        data = handler(self)
        return data["root"] if info.mode == "json" and isinstance(data, dict) else data

    @classmethod
    def model_modify_json_schema(cls, json_schema):
        return json_schema["properties"]["root"]

    def __iter__(self):
        return iter(self.root)

    def __len__(self) -> int:
        return len(self.root)

    def __getitem__(self, index: int) -> PointType:
        return self.root[index]

    def __setitem__(self, index: int, value: PointType):
        self.root[index] = value

    def __delitem__(self, index: int):
        del self.root[index]

    def __contains__(self, item) -> bool:
        return item in self.root

    def append(self, item: PointType):
        self.root.append(item)

    def insert(self, i: int, item: PointType):
        self.root.insert(i, item)

    def pop(self, i: int = -1):
        return self.root.pop(i)

    def remove(self, item: PointType):
        self.root.remove(item)

    def clear(self):
        self.root.clear()

    def count(self, item: PointType) -> int:
        return self.root.count(item)

    def index(self, item: PointType, *args):
        return self.root.index(item, *args)

    def reverse(self):
        self.root.reverse()

    def sort(self, /, *args, **kwds):
        self.root.sort(*args, **kwds)

    def extend(self, other: Union[PointList, list[PointType]]):
        if isinstance(other, PointList):
            self.root.extend(other.root)
        else:
            self.root.extend(other)
