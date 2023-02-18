TICK_RATE = 1470000


def position_to_ticks(position: int) -> int:
    return round(position / TICK_RATE)


def ticks_to_position(ticks: int) -> int:
    return ticks * TICK_RATE
