from typing import Iterable, List

import pypinyin
import regex as re

ENGLISH_CHARS = re.compile(r"[a-zA-Z]+")
CHINESE_RE = re.compile(r"\p{Han}")
WHITE_SPACE = re.compile(r"[\s\n\r\t]+")


def get_pinyin_series(
    chinese_series: Iterable[str],
    ignore_hyphens: bool = True,
    reverse_letters: bool = True,
    filter_non_chinese: bool = True,
) -> List[str]:
    chinese_list = list(chinese_series)
    pinyin_list = ["" for _ in range(len(chinese_list))]
    item_counts = [0 for _ in range(len(chinese_list))]
    result_items = []
    chinese = ""
    for i, part in enumerate(chinese_list):
        count = 0
        is_letter = False
        non_chinese = ""
        for char in part:
            if WHITE_SPACE.match(char) is not None or (ignore_hyphens and char == "-"):
                if len(non_chinese):
                    result_items.append(non_chinese)
                    count += 1
                    non_chinese = ""
            elif CHINESE_RE.match(char) is not None:
                if len(non_chinese):
                    result_items.append(non_chinese)
                    count += 1
                    non_chinese = ""
                chinese += char
                count += 1
            else:
                if len(chinese):
                    result_items.extend(
                        pypinyin.lazy_pinyin(chinese, errors=lambda x: " ")
                    )
                    chinese = ""
                if ENGLISH_CHARS.match(char) is not None:
                    if reverse_letters:
                        if len(non_chinese) and not is_letter:
                            result_items.append(non_chinese)
                            count += 1
                            non_chinese = ""
                        non_chinese += char
                        is_letter = True
                elif not filter_non_chinese:
                    if len(non_chinese) and is_letter:
                        result_items.append(non_chinese)
                        count += 1
                        non_chinese = ""
                    non_chinese += char
                    is_letter = False
        if len(non_chinese):
            result_items.append(non_chinese)
            count += 1
        item_counts[i] = count
    if len(chinese):
        result_items.extend(pypinyin.lazy_pinyin(chinese, errors=lambda x: " "))
    pinyin = ""
    index = 0
    for i in range(len(pinyin_list)):
        if item_counts[i] == 0:
            pinyin_list[i] = ""
            continue
        pinyin += result_items[index]
        index += 1
        for _ in range(1, item_counts[i]):
            if (
                result_items[index - 1][-1].isalnum()
                and result_items[index][0].isalnum()
            ):
                pinyin += " "
            pinyin += result_items[index]
            index += 1
        pinyin_list[i] = pinyin
        pinyin = ""
    return pinyin_list
