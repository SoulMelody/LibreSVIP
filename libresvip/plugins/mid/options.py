from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field

from libresvip.core.constants import DEFAULT_BPM


class MultiChannelOption(Enum):
    FIRST: Annotated[str, Field(title="仅导入首条通道")] = "first"
    SPLIT: Annotated[str, Field(title="全部拆分为轨道")] = "split"
    CUSTOM: Annotated[str, Field(title="自定义导入范围")] = "custom"


class InputOptions(BaseModel):
    import_lyrics: bool = Field(default=True, title="导入歌词")
    lyric_encoding: str = Field(
        default="utf-8",
        title="歌词编码",
        description="除非歌词出现乱码，否则不应更改此设置。",
    )
    import_time_signatures: bool = Field(
        default=True,
        title="导入拍号",
        description="关闭此选项，拍号设置为4/4。",
    )
    multi_channel: MultiChannelOption = Field(
        default=MultiChannelOption.FIRST,
        title="通道处理方式",
    )
    channels: str = Field(
        default="1",
        title="通道",
        description="指定要导入哪些通道上的音符。请输入通道的序号和/或通道范围（用英文逗号分隔），例如1,3,5-12。取值范围：1-16。仅在“通道处理方式”选项中选择“自定义导入范围”时有效。",
    )
    default_bpm: float = Field(
        default=DEFAULT_BPM, title="默认BPM", description="当MIDI文件中不存在BPM信息时，使用此值。"
    )


class OutputOptions(BaseModel):
    pre_shift: int = Field(
        default=0,
        title="拖拍前移补偿量",
        description="非负整数，单位为ticks。输入负数视为零。将发音为 y-、w-、a-、o- 和 e- 的音符提前，以缓解某些歌声合成软件半元音或元音音符出现迟滞的问题。推荐值：30~60。",
    )
    export_lyrics: bool = Field(default=True, title="导出歌词")
    remove_symbols: bool = Field(
        default=True,
        title="移除歌词中的常见标点符号",
        description="移除中英文的逗号、句号、问号和感叹号，防止不支持含标点符号歌词的歌声合成软件无法正常合成。",
    )
    compatible_lyric: bool = Field(
        default=False,
        title="歌词兼容性模式",
        description="将所有中文歌词转换为拼音，防止不支持导入带有中文歌词 MIDI 文件的歌声合成软件出现乱码。",
    )
    lyric_encoding: str = Field(
        default="utf-8",
        title="歌词编码",
        description="除非打开歌词兼容性模式后仍然乱码，否则不应更改此设置。",
    )
    transpose: int = Field(
        default=0,
        title="移调",
    )
    ticks_per_beat: int = Field(
        default=480,
        title="每拍ticks数",
        description="即 parts per quarter, 又名 ticks per quarter note，每四分音符的脉冲数。除非你知道这是什么，否则不应更改此设置。",
    )
