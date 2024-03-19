_colors = [
    "#b17ef3",
    "#da9de3",
    "#dd88d5",
    "#f57db7",
    "#dd8585",
    "#ebac99",
    "#f4a070",
    "#f1c970",
    "#c0cf63",
    "#99f07b",
    "#70d4b1",
    "#91bcdc",  # start
    "#96afef",
    "#979ae4",
]


def count_color() -> int:
    return len(_colors)


def get_color(index: int) -> str:
    return _colors[index % len(_colors)]
