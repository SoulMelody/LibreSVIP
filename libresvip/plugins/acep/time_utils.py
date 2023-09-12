from libresvip.utils import find_last_index

from .model import AcepTempo


def tick_to_second(tick: int, tempo_list: list[AcepTempo]) -> float:
    tempo_index = find_last_index(tempo_list, lambda tempo: tempo.position <= tick)
    if tempo_index <= 0:
        return tick / tempo_list[0].bpm / 8
    secs = 0.0
    secs += tempo_list[1].position / tempo_list[0].bpm / 8
    for i in range(1, tempo_index):
        secs += (
            (tempo_list[i + 1].position - tempo_list[i].position)
            / tempo_list[i].bpm
            / 8
        )
    secs += (tick - tempo_list[tempo_index].position) / tempo_list[tempo_index].bpm / 8
    return secs
