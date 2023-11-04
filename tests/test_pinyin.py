from libresvip.core.lyric_phoneme.chinese import get_pinyin_series


def test_pinyin_01(pinyin_example: list[str]) -> None:
    result = get_pinyin_series(pinyin_example)
    assert result == [
        "shan dong he ze",
        "cao xian",
        "niu pi",
        "wo di",
        "bao bei er",
        "xing zou",
        "hang ye",
        "",
    ]


def test_pinyin_02(pinyin_example: list[str]) -> None:
    result = get_pinyin_series(pinyin_example, False)
    assert result == [
        "shan dong he ze",
        "cao xian",
        "niu pi",
        "wo di",
        "bao bei er",
        "xing zou",
        "xing ye",
        "",
    ]


def test_pinyin_03(pinyin_example: list[str]) -> None:
    result = get_pinyin_series(pinyin_example, True, False)
    assert result == [
        "shan dong he ze",
        "cao xian",
        "niu",
        "wo di",
        "bao bei er",
        "xing zou",
        "hang ye",
        "",
    ]


def test_pinyin_04(pinyin_example: list[str]) -> None:
    result = get_pinyin_series(pinyin_example, False, False)
    assert result == [
        "shan dong he ze",
        "cao xian",
        "niu",
        "wo di",
        "bao bei er",
        "xing zou",
        "xing ye",
        "",
    ]


def test_pinyin_05(pinyin_example: list[str]) -> None:
    result = get_pinyin_series(pinyin_example, True, True, False)
    assert result == [
        "shan dong he ze",
        "cao xian，",
        "niu pi",
        "666 wo di",
        "bao bei er！",
        "xing zou",
        "hang ye",
        "",
    ]


def test_pinyin_06(pinyin_example: list[str]) -> None:
    result = get_pinyin_series(pinyin_example, False, True, False)
    assert result == [
        "shan dong he ze",
        "cao xian，",
        "niu pi",
        "666 wo di",
        "bao bei er！",
        "xing-zou-",
        "xing-ye-",
        "-",
    ]


def test_pinyin_07(pinyin_example: list[str]) -> None:
    result = get_pinyin_series(pinyin_example, True, False, False)
    assert result == [
        "shan dong he ze",
        "cao xian，",
        "niu",
        "666 wo di",
        "bao bei er！",
        "xing zou",
        "hang ye",
        "",
    ]


def test_pinyin_08(pinyin_example: list[str]) -> None:
    result = get_pinyin_series(pinyin_example, False, False, False)
    assert result == [
        "shan dong he ze",
        "cao xian，",
        "niu",
        "666 wo di",
        "bao bei er！",
        "xing-zou-",
        "xing-ye-",
        "-",
    ]
