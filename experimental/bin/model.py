# flake8: noqa: PLC2401
# LibreSVIP支持的格式疑似有点多了
from construct import (
    ExprAdapter,
    Float64l,
    GreedyBytes,
    GreedyRange,
    Int8ub,
    Int32ub,
    Prefixed,
    PrefixedArray,
    Struct,
    Switch,
    this,
)

from libresvip.core.compat import json

大市唱字符串 = ExprAdapter(
    PrefixedArray(
        Int32ub,
        ExprAdapter(
            Int32ub,
            encoder=lambda obj, ctx: ord(obj),
            decoder=lambda obj, ctx: chr(obj),
        ),
    ),
    encoder=lambda obj, ctx: obj.split(""),
    decoder=lambda obj, ctx: "".join(obj),
)

大市唱配置 = ExprAdapter(
    大市唱字符串,
    encoder=lambda obj, ctx: json.dumps(obj, separators=(",", ":")),
    decoder=lambda obj, ctx: json.loads(obj),
)


大市唱音频 = PrefixedArray(Int32ub, Float64l)


大市唱音量包络 = Struct(
    "名称" / 大市唱字符串,
    "内容"
    / Switch(
        this.名称,
        {
            "开始位置x": Prefixed(Int32ub, Float64l),
            "开始位置y": Prefixed(Int32ub, Float64l),
            "开始方向相对x": Prefixed(Int32ub, Float64l),
            "开始方向相对y": Prefixed(Int32ub, Float64l),
            "中间位置x": Prefixed(Int32ub, Float64l),
            "中间位置y": Prefixed(Int32ub, Float64l),
            "中间左方向相对x": Prefixed(Int32ub, Float64l),
            "中间左方向相对y": Prefixed(Int32ub, Float64l),
            "中间右方向相对x": Prefixed(Int32ub, Float64l),
            "中间右方向相对y": Prefixed(Int32ub, Float64l),
            "结束位置x": Prefixed(Int32ub, Float64l),
            "结束位置y": Prefixed(Int32ub, Float64l),
            "结束方向相对x": Prefixed(Int32ub, Float64l),
            "结束方向相对y": Prefixed(Int32ub, Float64l),
        },
        default=Prefixed(Int32ub, GreedyBytes),
    ),
)


大市唱发音小段 = Struct(
    "名称" / 大市唱字符串,
    "内容"
    / Switch(
        this.名称,
        {
            "类型": Prefixed(Int32ub, 大市唱字符串),
            "开始音标": Prefixed(Int32ub, 大市唱字符串),
            "开始辅音音标": Prefixed(Int32ub, 大市唱字符串),
            "结束音标": Prefixed(Int32ub, 大市唱字符串),
            "持续时间": Prefixed(Int32ub, Int32ub),
            "开始控制点时间": Prefixed(Int32ub, Float64l),
            "开始控制点频率": Prefixed(Int32ub, Float64l),
            "结束控制点时间": Prefixed(Int32ub, Float64l),
            "结束控制点频率": Prefixed(Int32ub, Float64l),
            "继续": Prefixed(Int32ub, Int8ub),
            "待续": Prefixed(Int32ub, Int8ub),
            "开始音符是爆破音不参与参数渐变": Prefixed(Int32ub, Int8ub),
            "结束音符是爆破音不参与参数渐变": Prefixed(Int32ub, Int8ub),
            "用于过度时使能": Prefixed(Int32ub, Int8ub),
            "清擦音实际长度": Prefixed(Int32ub, Int32ub),
            "用于过度时本音节的时间": Prefixed(Int32ub, Int32ub),
            "浊辅音前声带音音量": Prefixed(Int32ub, Float64l),
            "浊辅音前声带音实际长度": Prefixed(Int32ub, Int32ub),
            "音量包络": Prefixed(Int32ub, 大市唱音量包络),
        },
        default=Prefixed(Int32ub, GreedyBytes),
    ),
)


大市唱发音小段数组 = Struct(
    "名称" / 大市唱字符串,
    "内容"
    / Switch(
        this.名称,
        {"发音小段数组长度": Prefixed(Int32ub, Int32ub)},
        default=Prefixed(Int32ub, GreedyRange(大市唱发音小段)),
    ),
)

大市唱发音详细参数 = Struct(
    "名称" / 大市唱字符串,
    "内容"
    / Switch(
        this.名称,
        {
            "左附属发音小段数组": Prefixed(Int32ub, 大市唱发音小段数组),
            "核心发音小段数组": Prefixed(Int32ub, 大市唱发音小段数组),
            "右附属发音小段数组": Prefixed(Int32ub, 大市唱发音小段数组),
            "后面的音节过度发音小段": Prefixed(Int32ub, 大市唱发音小段),
        },
        default=Prefixed(Int32ub, GreedyBytes),
    ),
)

大市唱音节发音属性 = Struct(
    "名称" / 大市唱字符串,
    "内容"
    / Switch(
        this.名称,
        {
            "休止符": Prefixed(Int32ub, Int8ub),
            "词的结束": Prefixed(Int32ub, Int8ub),
            "左附属辅音": Prefixed(Int32ub, 大市唱字符串),
            "左核心辅音": Prefixed(Int32ub, 大市唱字符串),
            "核心元音": Prefixed(Int32ub, 大市唱字符串),
            "右核心辅音": Prefixed(Int32ub, 大市唱字符串),
            "右附属辅音": Prefixed(Int32ub, 大市唱字符串),
            "原生表音法的音节": Prefixed(Int32ub, 大市唱字符串),
            "音符显示": Prefixed(Int32ub, 大市唱字符串),
            "辅助显示": Prefixed(Int32ub, 大市唱字符串),
            "原文": Prefixed(Int32ub, 大市唱字符串),
            "核心左辅音可以借入": Prefixed(Int32ub, Int8ub),
            "核心左辅音是借入的": Prefixed(Int32ub, Int8ub),
            "右附属辅音可以借出": Prefixed(Int32ub, Int8ub),
            "右附属辅音已经借出": Prefixed(Int32ub, Int8ub),
            "左附属辅音可以去掉": Prefixed(Int32ub, Int8ub),
            "左附属辅音已经去掉": Prefixed(Int32ub, Int8ub),
            "右附属辅音可以去掉": Prefixed(Int32ub, Int8ub),
            "右附属辅音已经去掉": Prefixed(Int32ub, Int8ub),
            "核心左辅音可以借入的字符": Prefixed(Int32ub, 大市唱字符串),
            "后面连音数量": Prefixed(Int32ub, Int32ub),
            "原文重复序号": Prefixed(Int32ub, Int32ub),
            "分身": Prefixed(Int32ub, Int32ub),
            "句子中的位置": Prefixed(Int32ub, Int32ub),
            "发音详细参数": Prefixed(Int32ub, 大市唱发音详细参数),
        },
        default=Prefixed(Int32ub, GreedyBytes),
    ),
)

大市唱音符信息 = Struct(
    "名称" / 大市唱字符串,
    "内容"
    / Switch(
        this.名称,
        {
            "音高": Prefixed(Int32ub, Int32ub),
            "时长": Prefixed(Int32ub, Float64l),
            "连音": Prefixed(Int32ub, Int8ub),
            "左侧吐字自动": Prefixed(Int32ub, Int8ub),
            "右侧吐字自动": Prefixed(Int32ub, Int8ub),
            "左侧过度时长": Prefixed(Int32ub, Float64l),
            "左侧吐字延迟开始": Prefixed(Int32ub, Float64l),
            "左侧吐字建立耗时": Prefixed(Int32ub, Float64l),
            "右侧过度时长": Prefixed(Int32ub, Float64l),
            "右侧吐字消失耗时": Prefixed(Int32ub, Float64l),
            "右侧吐字提前结束": Prefixed(Int32ub, Float64l),
            "节拍结束": Prefixed(Int32ub, Int8ub),
            "短语结束": Prefixed(Int32ub, Int8ub),
            "音节发音": Prefixed(Int32ub, GreedyRange(大市唱音节发音属性)),
            "编曲修饰": Prefixed(Int32ub, PrefixedArray(Int32ub, 大市唱字符串)),
            "歌词": Prefixed(Int32ub, 大市唱字符串),
        },
        default=Prefixed(Int32ub, GreedyBytes),
    ),
)

大市唱技巧信息 = Struct(
    "名称" / 大市唱字符串,
    "内容"
    / Switch(
        this.名称,
        {
            "类型": Prefixed(Int32ub, 大市唱字符串),
            "开始": Prefixed(Int32ub, Float64l),
            "峰的时间": Prefixed(Int32ub, Float64l),
            "结束": Prefixed(Int32ub, Float64l),
            "峰值": Prefixed(Int32ub, Float64l),
            "峰尖锐": Prefixed(Int32ub, Float64l),
            "强度增加": Prefixed(Int32ub, Float64l),
            "频率增加": Prefixed(Int32ub, Float64l),
            "颤音速度": Prefixed(Int32ub, Float64l),
            "回音延迟": Prefixed(Int32ub, Float64l),
            "回音持续": Prefixed(Int32ub, Float64l),
        },
        default=Prefixed(Int32ub, GreedyBytes),
    ),
)

大市唱音符 = Struct(
    "名称" / 大市唱字符串,
    "内容"
    / Switch(
        this.名称,
        {"歌谱长度": Prefixed(Int32ub, Int32ub)},
        default=Prefixed(Int32ub, GreedyRange(大市唱音符信息)),
    ),
)

大市唱技巧 = Struct(
    "名称" / 大市唱字符串,
    "内容"
    / Switch(
        this.名称,
        {"技巧长度": Prefixed(Int32ub, Int32ub)},
        default=Prefixed(Int32ub, GreedyRange(大市唱技巧信息)),
    ),
)

大市唱轨道信息 = Struct(
    "名称" / 大市唱字符串,
    "内容"
    / Switch(
        this.名称,
        {
            "reader": Prefixed(Int32ub, Struct("角色或者乐器" / 大市唱字符串)),
            "note": Prefixed(Int32ub, GreedyRange(大市唱音符)),
            "skill": Prefixed(Int32ub, GreedyRange(大市唱技巧)),
            "小节的开始": Prefixed(Int32ub, Int8ub),
            "调号自动": Prefixed(Int32ub, Int8ub),
            "调号": Prefixed(Int32ub, Int32ub),
            "说唱": Prefixed(Int32ub, Int8ub),
            "自然段开始": Prefixed(Int32ub, Int8ub),
            "高潮开始": Prefixed(Int32ub, Int8ub),
            "纯音乐": Prefixed(Int32ub, Int8ub),
            "纯朗读": Prefixed(Int32ub, Int8ub),
            "声乐曲音量": Prefixed(Int32ub, Float64l),
            "声乐曲清擦相对音量": Prefixed(Int32ub, Float64l),
            "编曲修饰音量": Prefixed(Int32ub, Float64l),
            "打节拍旋律音量": Prefixed(Int32ub, Float64l),
            "打节拍鼓音量": Prefixed(Int32ub, Float64l),
            "每分钟拍数": Prefixed(Int32ub, Int32ub),
            "节拍配置名称": Prefixed(Int32ub, 大市唱字符串),
            "语种": Prefixed(Int32ub, 大市唱字符串),
            "声乐清擦": Prefixed(Int32ub, 大市唱音频),
            "声乐声带": Prefixed(Int32ub, 大市唱音频),
            "编曲修饰": Prefixed(Int32ub, 大市唱音频),
            "打节拍旋律": Prefixed(Int32ub, 大市唱音频),
            "打节拍鼓": Prefixed(Int32ub, 大市唱音频),
        },
        default=Prefixed(Int32ub, GreedyBytes),
    ),
)

大市唱文件格式 = Struct(
    "魔数" / 大市唱字符串,
    "版本号" / Int32ub,
    "歌名" / 大市唱字符串,
    "文件名" / 大市唱字符串,
    "作者" / 大市唱字符串,
    "公司" / 大市唱字符串,
    "说明" / 大市唱字符串,
    "采样频率" / Int32ub,
    "正在编辑的轨道的索引" / Int32ub,
    "轨道" / PrefixedArray(Int32ub, Prefixed(Int32ub, GreedyRange(大市唱轨道信息))),
    "音色配置" / Prefixed(Int32ub, GreedyBytes),
    "打节拍配置" / 大市唱配置,
    "编曲配置" / 大市唱配置,
    "语种"
    / PrefixedArray(
        Int32ub,
        Struct(
            "语言" / 大市唱字符串,
            "语言配置" / 大市唱配置,
        ),
    ),
)
