from __future__ import annotations

import dataclasses
import operator
from bisect import bisect_right
from collections.abc import Mapping
from functools import reduce, singledispatchmethod
from typing import TYPE_CHECKING

import portion

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable

    UnaryFunction = Callable[[int | float], float]
    UnaryFunctionOrConstant = UnaryFunction | int | float


@dataclasses.dataclass(frozen=True)
class _AtomicInterval:
    start: float
    end: float
    left_closed: bool
    right_closed: bool
    value: UnaryFunctionOrConstant

    def contains(self, x: float) -> bool:
        left_ok = x > self.start or (self.left_closed and x == self.start)
        right_ok = x < self.end or (self.right_closed and x == self.end)
        return left_ok and right_ok


class PiecewiseIntervalDict(portion.IntervalDict):
    def __init__(
        self,
        mapping_or_iterable: Mapping[portion.Interval, UnaryFunctionOrConstant]
        | Iterable[tuple[portion.Interval, UnaryFunctionOrConstant]]
        | None = None,
    ) -> None:
        super().__init__(mapping_or_iterable=mapping_or_iterable)
        self._last_index = 0

    def _get_func(self, x: float) -> UnaryFunctionOrConstant | None:
        _last_index = self._last_index
        while _last_index < len(self._storage._list):
            boundary, func = self._storage.peekitem(_last_index)
            if x in boundary:
                self._last_index = _last_index
                return func
            elif x < boundary:
                self._last_index = _last_index
                break
            _last_index += 1

    def __setitem__(self, key: portion.Interval | float, value: UnaryFunctionOrConstant) -> None:
        if isinstance(key, portion.Interval):
            interval = key
        else:
            interval = self._klass.from_atomic(portion.Bound.CLOSED, key, key, portion.Bound.CLOSED)

        if interval.empty:
            return

        self._storage[interval] = value

    def __getitem__(self, key: portion.Interval | float) -> UnaryFunctionOrConstant | None:
        if isinstance(key, portion.Interval):
            return super().__getitem__(key)
        elif (func := self._get_func(key)) is not None:
            return func(key) if callable(func) else func
        raise KeyError(key)


class BisectIntervalMap:
    def __init__(
        self,
        mapping_or_iterable: Mapping[portion.Interval, UnaryFunctionOrConstant]
        | Iterable[tuple[portion.Interval, UnaryFunctionOrConstant]]
        | None = None,
    ) -> None:
        self._segments: list[_AtomicInterval] = []
        self._starts: list[float] = []
        self._last_index = 0
        if mapping_or_iterable is not None:
            if isinstance(mapping_or_iterable, Mapping):
                items = mapping_or_iterable.items()
            else:
                items = mapping_or_iterable
            for key, value in items:
                self[key] = value

    @staticmethod
    def _from_interval(
        interval: portion.Interval, value: UnaryFunctionOrConstant
    ) -> _AtomicInterval:
        data = portion.to_data(interval)
        if len(data) != 1:
            msg = "Only atomic intervals are supported"
            raise ValueError(msg)
        _, start, end, _ = data[0]
        return _AtomicInterval(
            start=float(start),
            end=float(end),
            left_closed=interval.left == portion.Bound.CLOSED,
            right_closed=interval.right == portion.Bound.CLOSED,
            value=value,
        )

    @staticmethod
    def _to_interval(segment: _AtomicInterval) -> portion.Interval:
        if segment.left_closed and segment.right_closed:
            return portion.closed(segment.start, segment.end)
        if segment.left_closed and not segment.right_closed:
            return portion.closedopen(segment.start, segment.end)
        if not segment.left_closed and segment.right_closed:
            return portion.openclosed(segment.start, segment.end)
        return portion.open(segment.start, segment.end)

    def _rebuild_starts(self) -> None:
        self._starts = [segment.start for segment in self._segments]

    def _remove_overlap(self, interval: portion.Interval) -> None:
        new_segments: list[_AtomicInterval] = []
        for segment in self._segments:
            remaining = self._to_interval(segment) - interval
            for atomic in portion.to_data(remaining):
                bound_left, start, end, bound_right = atomic
                if start == end and not bound_left and not bound_right:
                    continue
                new_segments.append(
                    _AtomicInterval(
                        start=float(start),
                        end=float(end),
                        left_closed=bound_left,
                        right_closed=bound_right,
                        value=segment.value,
                    )
                )
        self._segments = new_segments

    def __setitem__(self, key: portion.Interval | float, value: UnaryFunctionOrConstant) -> None:
        interval = key if isinstance(key, portion.Interval) else portion.closed(key, key)
        if interval.empty:
            return
        self._remove_overlap(interval)
        self._segments.append(self._from_interval(interval, value))
        self._segments.sort(
            key=lambda segment: (segment.start, not segment.left_closed, segment.end)
        )
        self._rebuild_starts()
        self._last_index = 0

    def _find_index(self, x: float) -> int:
        if not self._segments:
            return -1
        idx = min(self._last_index, len(self._segments) - 1)
        if self._segments[idx].contains(x):
            return idx
        if x >= self._segments[idx].start:
            while idx + 1 < len(self._segments) and x >= self._segments[idx + 1].start:
                idx += 1
                if self._segments[idx].contains(x):
                    self._last_index = idx
                    return idx
        idx = bisect_right(self._starts, x) - 1
        if idx < 0:
            return -1
        if self._segments[idx].contains(x):
            return idx
        if idx > 0 and self._segments[idx].start == x and self._segments[idx - 1].contains(x):
            return idx - 1
        return -1

    def __getitem__(self, key: portion.Interval | float) -> UnaryFunctionOrConstant | None:
        if isinstance(key, portion.Interval):
            msg = "Interval lookup is not supported"
            raise TypeError(msg)
        idx = self._find_index(key)
        if idx < 0:
            raise KeyError(key)
        self._last_index = idx
        value = self._segments[idx].value
        return value(key) if callable(value) else value

    def get(
        self, key: float, default: UnaryFunctionOrConstant | None = None
    ) -> UnaryFunctionOrConstant | None:
        idx = self._find_index(key)
        if idx < 0:
            return default
        self._last_index = idx
        value = self._segments[idx].value
        return value(key) if callable(value) else value


@dataclasses.dataclass
class RangeInterval:
    _sub_ranges: dataclasses.InitVar[list[tuple[int, int]] | None] = None
    interval: portion.Interval = dataclasses.field(init=False)

    def __post_init__(self, _sub_ranges: list[tuple[int, int]] | None) -> None:
        self.interval = reduce(
            operator.or_,
            (portion.closedopen(*sub_range) for sub_range in (_sub_ranges or [])),
            portion.empty(),
        )

    def is_empty(self) -> bool:
        return self.interval.empty

    def sub_ranges(self) -> Iterable[tuple[int, int]]:
        for sub_range in portion.to_data(self.interval):
            yield int(sub_range[1]), int(sub_range[2])

    def sub_range_including(self, value: int) -> tuple[int, int] | None:
        for sub_range in self.interval:
            if value in sub_range:
                sub_range_data = portion.to_data(sub_range)
                return sub_range_data[1], sub_range_data[2]
        return None

    def includes(self, value: int) -> bool:
        return value in self.interval

    def __contains__(self, interval: RangeInterval | int) -> bool:
        if isinstance(interval, RangeInterval):
            interval = interval.interval
        return interval in self.interval

    def intersection(self, interval: RangeInterval) -> RangeInterval:
        new_interval = RangeInterval()
        new_interval.interval = self.interval & interval.interval
        return new_interval

    def union(self, interval: RangeInterval) -> RangeInterval:
        new_interval = RangeInterval()
        new_interval.interval = self.interval | interval.interval
        return new_interval

    def sub(self, interval: RangeInterval) -> RangeInterval:
        new_interval = RangeInterval()
        new_interval.interval = self.interval - interval.interval
        return new_interval

    def complement(self, complete_interval: RangeInterval) -> RangeInterval:
        new_interval = RangeInterval()
        new_interval.interval = complete_interval.interval - self.interval
        return new_interval

    @singledispatchmethod
    def expand(self, a: tuple[int, int] | int) -> RangeInterval:
        raise NotImplementedError

    @expand.register(tuple)
    def _(self, radius_tuple: tuple[int, int]) -> RangeInterval:
        return RangeInterval(
            [
                (
                    sub_range[0] - radius_tuple[0],
                    sub_range[1] + radius_tuple[1],
                )
                for sub_range in self.sub_ranges()
            ]
        )

    @expand.register(int)
    def _(self, radius: int) -> RangeInterval:
        return self.expand((radius, radius))

    @singledispatchmethod
    def shrink(self, a: tuple[int, int] | int) -> RangeInterval:
        raise NotImplementedError

    @shrink.register(int)
    def _(self, radius: int) -> RangeInterval:
        return self.expand((-radius, -radius))

    @shrink.register(tuple)
    def _(self, radius_tuple: tuple[int, int]) -> RangeInterval:
        return self.expand((-radius_tuple[0], -radius_tuple[1]))

    def shift(self, offset: int) -> RangeInterval:
        return RangeInterval(
            [(sub_range[0] + offset, sub_range[1] + offset) for sub_range in self.sub_ranges()]
        )

    def __and__(self, other: RangeInterval) -> RangeInterval:
        return self.intersection(other)

    def __or__(self, other: RangeInterval) -> RangeInterval:
        return self.union(other)

    def __sub__(self, other: RangeInterval) -> RangeInterval:
        return self.sub(other)

    def __xor__(self, other: RangeInterval) -> RangeInterval:
        return (self | other) - (self & other)

    def __rshift__(self, other: int) -> RangeInterval:
        return self.shift(other)

    def __lshift__(self, other: int) -> RangeInterval:
        return self.shift(-other)
