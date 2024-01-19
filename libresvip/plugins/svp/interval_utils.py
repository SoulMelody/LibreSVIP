from .constants import TICK_RATE


def position_to_ticks(position: int) -> int:
    return round(position / TICK_RATE)


def ticks_to_position(ticks: int) -> int:
    return ticks * TICK_RATE
