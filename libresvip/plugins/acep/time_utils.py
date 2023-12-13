import more_itertools

from .model import AcepTempo


def tick_to_second(tick: int, tempo_list: list[AcepTempo]) -> float:
    secs = 0.0
    if len(tempo_list) == 1:
        tempo = tempo_list[0]
    else:
        for tempo, next_tempo in more_itertools.pairwise(tempo_list):
            if tick <= next_tempo.position:
                break
            secs += (next_tempo.position - tempo.position) / tempo.bpm / 8
        else:
            tempo = next_tempo
    if tick < tempo.position:
        return tick / tempo.bpm / 8
    secs += (tick - tempo.position) / tempo.bpm / 8
    return secs


def second_to_tick(second: float, tempo_list: list[AcepTempo]) -> int:
    secs = 0.0
    if len(tempo_list) == 1:
        tempo = tempo_list[0]
    else:
        for tempo, next_tempo in more_itertools.pairwise(tempo_list):
            next_secs = secs + ((next_tempo.position - tempo.position) / tempo.bpm / 8)
            if second <= next_secs:
                break
            secs = next_secs
        else:
            tempo = next_tempo
    if second < secs:
        return round(second * tempo.bpm * 8)
    return tempo.position + round((second - secs) * tempo.bpm * 8)
