from enum import Enum
from typing import Annotated

from pydantic import BaseSettings, Field


class BreathOption(Enum):
    IGNORE: Annotated[str, Field(title="忽略所有换气音符")] = "ignore"
    KEEP: Annotated[str, Field(title="保留为普通音符")] = "keep"
    CONVERT: Annotated[str, Field(title="转换为换气标记")] = "convert"


class GroupOption(Enum):
    SPLIT: Annotated[
        str, Field(title="全部拆分为轨道", description="为每个音符组引用生成一个单独的音轨")
    ] = "split"
    MERGE: Annotated[
        str, Field(title="保留原始位置", description="仅在出现音符重叠时将音符组拆分至单独的音轨")
    ] = "merge"


class PitchOption(Enum):
    FULL: Annotated[
        str, Field(title="输入完整音高曲线", description="不论是否经过编辑，均输入整条音高曲线")
    ] = "full"
    VIBRATO: Annotated[
        str, Field(title="仅输入已编辑部分（颤音模式）", description="仅输入已编辑部分的音高曲线；未经编辑的默认颤音也将被导入")
    ] = "vibrato"
    PLAIN: Annotated[
        str, Field(title="仅输入已编辑部分（平整模式）", description="仅输入已编辑部分的音高曲线；未经编辑的默认颤音将被忽略")
    ] = "plain"


class VibratoOption(Enum):
    NONE: Annotated[
        str, Field(title="全部抹平", description="所有音符的颤音深度将被设置为 0，以保证输出的音高曲线与输入一致")
    ] = "none"
    ALWAYS: Annotated[
        str, Field(title="全部保留", description="保持所有音符的默认颤音，但可能造成输入与输出音高曲线不一致")
    ] = "always"
    HYBRID: Annotated[
        str, Field(title="混合保留", description="在输入音高被编辑过的区域去除颤音，其余部分保留默认颤音")
    ] = "hybrid"


class InputOptions(BaseSettings):
    instant: bool = Field(
        default=True,
        title="遵循即时音高模式设置",
        description="关闭此选项时，无论工程文件是否开启了即时音高模式，都只会考虑原始的默认音高。若您基于即时音高模式进行了调校，建议打开此选项。",
    )
    pitch: PitchOption = Field(
        default=PitchOption.PLAIN,
        title="音高信息输入模式",
        description="本选项控制音高曲线被导入的范围和判定条件。其中“经过编辑”的定义为：参数面板中的音高偏差、颤音包络和音符属性中的音高转变、颤音中的任意一项经过编辑。",
    )
    breath: BreathOption = Field(
        default=BreathOption.CONVERT,
        title="换气音符处理方式",
    )
    group: GroupOption = Field(
        default=GroupOption.SPLIT,
        title="音符组导入方式",
        description="注意：若音符组较多，请尽量选择“保留原始位置”以防止轨道数量暴增。但若音符组之间、音符组与主组之间存在时间轴上紧挨（但不重叠）的音符，则建议选择“拆分为轨道”以确保段落划分不被破坏。",
    )


class OutputOptions(BaseSettings):
    vibrato: VibratoOption = Field(default=VibratoOption.NONE, title="自动颤音处理方式")
    down_sample: int = Field(
        default=40,
        title="设置参数点的平均采样间隔以改善性能（0 为无限制）",
        description="减小采样间隔可提高参数曲线的精准度，但可能造成渲染卡顿（例如 Synthesizer V Studio Pro + AI 声库）。请根据硬件配置与实际体验酌情设置此值。",
    )
