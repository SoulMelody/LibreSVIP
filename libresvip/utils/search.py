from collections.abc import Callable
from typing import Optional, TypeVar

from more_itertools import locate, rlocate

T = TypeVar("T")


def find_index(obj_list: list[T], pred: Callable[[T], bool]) -> int:
    return next(locate(obj_list, pred), -1)


def find_last_index(obj_list: list[T], pred: Callable[[T], bool]) -> int:
    return next(rlocate(obj_list, pred), -1)


def binary_find_first(n: list[T], pred: Callable[[T], bool]) -> Optional[T]:
    if not len(n):
        return None
    left, right = 0, len(n) - 1
    while right > left:
        middle = (left + right) // 2
        if pred(n[middle]):
            right = middle
        else:
            left = middle + 1
    return n[right] if pred(n[right]) else None


def binary_find_last(n: list[T], pred: Callable[[T], bool]) -> Optional[T]:
    if not len(n):
        return None
    left, right = 0, len(n) - 1
    while right > left:
        middle = (left + right + 1) // 2
        if pred(n[middle]):
            left = middle
        else:
            right = middle - 1
    return n[left] if pred(n[left]) else None
