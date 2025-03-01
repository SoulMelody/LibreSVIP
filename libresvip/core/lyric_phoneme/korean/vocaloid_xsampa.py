from ko_pron.ko_pron import decompose_syllable, romanise

romaji2korean_xsampa = {
    "": "",
    "a": "a",
    "ya": "ja",
    "eo": "7",
    "yeo": "j7",
    "ae": "e",
    "e": "e",
    "yae": "je",
    "ye": "je",
    "o": "o",
    "wa": "oa",
    "yo": "jo",
    "u": "u",
    "weo": "u7",
    "wae": "ue",
    "we": "ue",
    "oe": "ue",
    "wi": "ui",
    "eu": "M",
    "eui": "Mi",
    "i": "i",
    "g": "g",
    "gg": "g'",
    "n": "n",
    "d": "d",
    "dd": "d'",
    "r": "r",
    "l": "l",
    "m": "m",
    "b": "b",
    "bb": "b'",
    "s": "s",
    "ss": "s'",
    "j": "c",
    "jj": "c'",
    "ch": "ch",
    "k": "k",
    "t": "t",
    "p": "p",
    "h": "h",
    "ng": "Np",
    "gs": "gp",
    "nch": "np",
    "nh": "np",
    "kk": "g'",
    "tt": "d'",
    "pp": "b'",
    "wo": "a",
    "yu": "ju",
    "ui": "i",
    "lg": "gp",
    "lm": "mp",
    "lb": "rp",
    "ls": "rp",
    "lt": "rp",
    "lp": "bp",
    "lh": "rp",
    "ps": "bp",
}

romaji2korean_xsampa_final = {
    "k": "gp",
    "n": "np",
    "t": "dp",
    "l": "rp",
    "m": "mp",
    "p": "bp",
}


def hangul2xsampa(lyric: str) -> str:
    phonemes = []
    for each in decompose_syllable(lyric):
        if isinstance(each, dict):
            initial_romaji = romanise(each["initial"], "rr")
            vowel_romaji = romanise(each["vowel"], "rr")
            final_romaji = romanise(each["final"], "rr")
            initial_xsampa = romaji2korean_xsampa.get(initial_romaji, "")
            vowel_xsampa = romaji2korean_xsampa.get(vowel_romaji, "")
            final_xsampa = romaji2korean_xsampa.get(final_romaji, "")
            if initial_xsampa in ["s", "sh"] and vowel_xsampa.startswith(("i", "y", "j")):
                initial_xsampa = "sh" if initial_xsampa == "s" else "sh'"
            elif vowel_xsampa in ["s", "sh"] and final_xsampa.startswith(("i", "y", "j")):
                vowel_xsampa = "sh" if vowel_xsampa == "s" else "sh'"
            if final_xsampa in romaji2korean_xsampa_final:
                final_xsampa = romaji2korean_xsampa_final[final_xsampa]
            phonemes.append(f"{initial_xsampa} {vowel_xsampa} {final_xsampa}".strip())
    return " ".join(phonemes) if phonemes else "r a"
