from typing import Callable, List, Optional, TypeVar

T = TypeVar("T")


def binary_find_first(n: List[T], pred: Callable[[T], bool]) -> Optional[T]:
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


def binary_find_last(n: List[T], pred: Callable[[T], bool]) -> Optional[T]:
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
