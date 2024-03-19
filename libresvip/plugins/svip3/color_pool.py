import random

_colors = [
    "#24936E",
    "#B54434",
    "#B5495B",
    "#A8497A",
    "#4F726C",
    "#939650",
    "#CA7A2C",
    "#DB4D6D",
    "#77428D",
    "#005CAF",
]


def count_color() -> int:
    return len(_colors)


def get_color(index: int) -> str:
    return _colors[index % len(_colors)]


def random_color() -> str:
    return random.choice(_colors)
