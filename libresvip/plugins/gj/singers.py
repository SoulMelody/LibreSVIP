from bidict import bidict

DEFAULT_SINGER = "扇宝"
DEFAULT_SINGER_ID = "513singer"


singer2id = bidict(
    {
        "扇宝": "513singer",
        "SING-林嘉慧": "514singer",
        "Rocky": "881singer",
        "杨超越": "ycysinger",
    },
)

id2singer = singer2id.inverse
