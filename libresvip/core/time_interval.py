from __future__ import annotations

import dataclasses
import operator
from functools import reduce, singledispatchmethod
from typing import TYPE_CHECKING, Optional, Union

import portion

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Mapping

    UnaryFunction = Callable[[Union[int, float]], float]
    UnaryFunctionOrConstant = Union[UnaryFunction, int, float]


class PiecewiseIntervalDict(portion.IntervalDict):
    def __init__(
        self,
        mapping_or_iterable: Optional[
            Union[
                Mapping[portion.Interval, UnaryFunctionOrConstant],
                Iterable[tuple[portion.Interval, UnaryFunctionOrConstant]],
            ]
        ] = None,
    ) -> None:
        super().__init__(mapping_or_iterable=mapping_or_iterable)
        self._last_index = 0

    def _get_func(self, x: float) -> Optional[UnaryFunctionOrConstant]:
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

    def __setitem__(self, key: portion.Interval, value: UnaryFunctionOrConstant) -> None:
        if isinstance(key, portion.Interval):
            interval = key
        else:
            interval = self._klass.from_atomic(portion.Bound.CLOSED, key, key, portion.Bound.CLOSED)

        if interval.empty:
            return

        self._storage[interval] = value

    def __getitem__(self, key: Union[portion.Interval, float]) -> Optional[UnaryFunctionOrConstant]:
        if isinstance(key, portion.Interval):
            return super().__getitem__(key)
        elif (func := self._get_func(key)) is not None:
            return func(key) if callable(func) else func
        raise KeyError(key)


@dataclasses.dataclass
class RangeInterval:
    _sub_ranges: dataclasses.InitVar[Optional[list[tuple[int, int]]]] = None
    interval: portion.Interval = dataclasses.field(init=False)

    def __post_init__(self, _sub_ranges: Optional[list[tuple[int, int]]]) -> None:
        self.interval = reduce(
            operator.or_,
            (portion.closedopen(*sub_range) for sub_range in (_sub_ranges or [])),
            portion.empty(),
        )

    def is_empty(self) -> bool:
        return self.interval.empty

    def sub_ranges(self) -> Iterable[tuple[int, int]]:
        for sub_range in portion.to_data(self.interval):
            yield sub_range[1], sub_range[2]

    def sub_range_including(self, value: int) -> Optional[tuple[int, int]]:
        for sub_range in self.interval:
            if value in sub_range:
                sub_range_data = portion.to_data(sub_range)
                return sub_range_data[1], sub_range_data[2]
        return None

    def includes(self, value: int) -> bool:
        return value in self.interval

    def __contains__(self, interval: Union[RangeInterval, int]) -> bool:
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
    def expand(self, a: Union[tuple[int, int], int]) -> RangeInterval:
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
    def shrink(self, a: Union[tuple[int, int], int]) -> RangeInterval:
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
