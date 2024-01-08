from collections import defaultdict

DEFAULT_SINGER = "扇宝"
DEFAULT_SINGER_ID = "513singer"


singer2id = defaultdict(
    lambda: DEFAULT_SINGER_ID,
    {
        "扇宝": "513singer",
        "SING-林嘉慧": "514singer",
        "Rocky": "881singer",
        "杨超越": "ycysinger",
    },
)

id2singer = defaultdict(lambda: DEFAULT_SINGER, {value: key for key, value in singer2id.items()})
