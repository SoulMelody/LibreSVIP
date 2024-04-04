from bidict import bidict

DEFAULT_SINGER = "然糊糊"
DEFAULT_SINGER_ID = 26
DEFAULT_SEED = 23

id2singer = bidict(
    {
        1: "小莫",
        2: "小夜",
        5: "火涟",
        6: "云灏",
        7: "楚瓷",
        8: "橘",
        9: "鲤沅",
        10: "嗒啦啦",
        11: "绮萱",
        12: "雀河",
        13: "文栗",
        14: "长歌",
        15: "鸾明",
        16: "荼鸢",
        17: "柊雪",
        18: "洛天依",
        19: "起复",
        20: "起礼",
        21: "波音リツ",
        22: "绯",
        24: "Steel",
        25: "Ghost",
        26: "然糊糊",
        27: "Bianca",
        28: "Lien",
        29: "David",
        30: "褚明",
        31: "Barber",
        33: "缇",
        34: "黑昂宿",
        35: "燈凛",
        36: "緋惺",
        37: "六歌",
        39: "唐青乐",
        40: "Sidney",
        41: "Naples",
        1006: "言和",
        1007: "乐正绫",
        1011: "乐正龙牙",
        1012: "墨清弦",
        1013: "徵羽摩柯",
        2001: "川",
        3006: "Rowly G.",
        5038: "空诗音Lemi",
    },
)

singer2id = id2singer.inverse

singer2seed = bidict(
    {
        1: "小莫",
        2: "小夜",
        3: "火涟",
        4: "云灏",
        5: "楚瓷",
        6: "橘",
        7: "鲤沅",
        8: "嗒啦啦",
        9: "绮萱",
        10: "雀河",
        11: "文栗",
        12: "长歌",
        13: "鸾明",
        14: "荼鸢",
        15: "柊雪",
        16: "洛天依",
        17: "起复",
        18: "起礼",
        19: "波音リツ",
        20: "绯",
        21: "Steel",
        22: "Ghost",
        23: "然糊糊",
        24: "Bianca",
        25: "Lien",
        26: "David",
        27: "褚明",
        28: "Barber",
        29: "缇",
        30: "黑昂宿",
        31: "Rowly G.",
        32: "乐正绫",
        33: "言和",
        # 34: "葵栀",
        # 35: "李奕",
        # 36: "70D",
        # 37: "福姬彩华",
        38: "川",
        # 39: "X先生",
        # 40: "福姬彩华-明亮",
        # 41: "福姬彩华-暗淡",
        43: "乐正龙牙",
        46: "燈凛",
        47: "緋惺",
        48: "六歌",
        51: "唐青乐",
        57: "Sidney",
        58: "Naples",
        60: "墨清弦",
        61: "徵羽摩柯",
        87: "空诗音Lemi",
    },
).inverse
