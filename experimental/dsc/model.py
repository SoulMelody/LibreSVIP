from dataclasses import dataclass, field
from typing import Optional, Union


@dataclass
class 大市唱字典:
    class Meta:
        name = "字典"

    语种: Optional[str] = field(
        default=None,
        metadata={
            "name": "_3093",
            "type": "Element",
            "required": True,
        },
    )
    内容: list[object] = field(
        default_factory=list,
        metadata={
            "name": "_926",
            "type": "Element",
            "min_occurs": 1,
        },
    )


@dataclass
class 大市唱打节拍:
    class Meta:
        name = "打节拍"

    名称: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    颜色: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    风格: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    节拍乐器: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    打击乐器: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class 大市唱技巧:
    class Meta:
        name = "技巧"

    类型: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    开始: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    峰的时间: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    结束: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    峰值: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    峰尖锐: Optional[Union[int, float]] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    回音延迟: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    回音持续: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    强度增加: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    频率增加: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )


@dataclass
class 大市唱控制点数组:
    class Meta:
        name = "控制点数组"

    m倍频: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    m最大值: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    m最小值: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    m开始x: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    m峰的x: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    m结束x: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    m左尖锐: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    m右尖锐: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    m增加: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    m峰值: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    m值: Optional[Union[float, int]] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )


@dataclass
class 大市唱滤波:
    最小值: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    最大值: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    只能为正: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    上下对称: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    控制点数组: list[大市唱控制点数组] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )


@dataclass
class 大市唱编曲:
    class Meta:
        name = "编曲"

    musica_array_length: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_0_music_sheet_type: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_0_user_define_instrument_0: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_0_user_define_instrument_1: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_0_user_define_instrument_2: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_0_user_define_instrument_3: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_0_user_define_instrument_4: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_0_user_define_instrument_5: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_0_user_define_instrument_6: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_0_user_define_instrument_7: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_0_user_define_volume: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_0_user_define_align_point: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_0_user_define_music_sheet_length: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_0_user_define_music_sheet_0_instrument_index: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_0_user_define_music_sheet_0_pitch: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_0_user_define_music_sheet_0_start: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_0_user_define_music_sheet_0_duration: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_0_user_define_music_sheet_0_strength: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_0_user_define_music_sheet_1_instrument_index: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_0_user_define_music_sheet_1_pitch: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_0_user_define_music_sheet_1_start: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_0_user_define_music_sheet_1_duration: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_0_user_define_music_sheet_1_strength: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_0_user_define_music_sheet_2_instrument_index: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_0_user_define_music_sheet_2_pitch: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_0_user_define_music_sheet_2_start: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_0_user_define_music_sheet_2_duration: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_0_user_define_music_sheet_2_strength: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_0_echo_instrument: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_0_echo_volume: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_0_name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_0_color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_0_type: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_0_align: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_1_music_sheet_type: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_1_user_define_instrument_0: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_1_user_define_instrument_1: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_1_user_define_instrument_2: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_1_user_define_instrument_3: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_1_user_define_instrument_4: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_1_user_define_instrument_5: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_1_user_define_instrument_6: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_1_user_define_instrument_7: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_1_user_define_volume: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_1_user_define_align_point: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_1_user_define_music_sheet_length: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_1_echo_instrument: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_1_echo_volume: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_1_name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_1_color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_1_type: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_1_align: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_2_music_sheet_type: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_2_user_define_instrument_0: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_2_user_define_instrument_1: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_2_user_define_instrument_2: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_2_user_define_instrument_3: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_2_user_define_instrument_4: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_2_user_define_instrument_5: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_2_user_define_instrument_6: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_2_user_define_instrument_7: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_2_user_define_volume: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_2_user_define_align_point: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_2_user_define_music_sheet_length: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_2_echo_instrument: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_2_echo_volume: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_2_name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_2_color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_2_type: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_2_align: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_3_music_sheet_type: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_3_user_define_instrument_0: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_3_user_define_instrument_1: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_3_user_define_instrument_2: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_3_user_define_instrument_3: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_3_user_define_instrument_4: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_3_user_define_instrument_5: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_3_user_define_instrument_6: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_3_user_define_instrument_7: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_3_user_define_volume: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_3_user_define_align_point: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_3_user_define_music_sheet_length: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_3_user_define_music_sheet_0_instrument_index: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_3_user_define_music_sheet_0_pitch: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_3_user_define_music_sheet_0_start: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_3_user_define_music_sheet_0_duration: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_3_user_define_music_sheet_0_strength: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_3_user_define_music_sheet_1_instrument_index: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_3_user_define_music_sheet_1_pitch: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_3_user_define_music_sheet_1_start: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_3_user_define_music_sheet_1_duration: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_3_user_define_music_sheet_1_strength: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_3_user_define_music_sheet_2_instrument_index: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_3_user_define_music_sheet_2_pitch: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_3_user_define_music_sheet_2_start: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_3_user_define_music_sheet_2_duration: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_3_user_define_music_sheet_2_strength: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_3_user_define_music_sheet_3_instrument_index: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_3_user_define_music_sheet_3_pitch: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_3_user_define_music_sheet_3_start: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_3_user_define_music_sheet_3_duration: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_3_user_define_music_sheet_3_strength: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_3_user_define_music_sheet_4_instrument_index: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_3_user_define_music_sheet_4_pitch: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_3_user_define_music_sheet_4_start: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_3_user_define_music_sheet_4_duration: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_3_user_define_music_sheet_4_strength: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_3_user_define_music_sheet_5_instrument_index: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_3_user_define_music_sheet_5_pitch: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_3_user_define_music_sheet_5_start: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_3_user_define_music_sheet_5_duration: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_3_user_define_music_sheet_5_strength: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_3_echo_instrument: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_3_echo_volume: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_3_name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_3_color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_3_type: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_3_align: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_4_music_sheet_type: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_4_user_define_instrument_0: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_4_user_define_instrument_1: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_4_user_define_instrument_2: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_4_user_define_instrument_3: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_4_user_define_instrument_4: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_4_user_define_instrument_5: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_4_user_define_instrument_6: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_4_user_define_instrument_7: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_4_user_define_volume: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_4_user_define_align_point: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_4_user_define_music_sheet_length: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_4_user_define_music_sheet_0_instrument_index: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_4_user_define_music_sheet_0_pitch: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_4_user_define_music_sheet_0_start: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_4_user_define_music_sheet_0_duration: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_4_user_define_music_sheet_0_strength: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_4_user_define_music_sheet_1_instrument_index: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_4_user_define_music_sheet_1_pitch: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_4_user_define_music_sheet_1_start: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_4_user_define_music_sheet_1_duration: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_4_user_define_music_sheet_1_strength: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_4_user_define_music_sheet_2_instrument_index: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_4_user_define_music_sheet_2_pitch: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_4_user_define_music_sheet_2_start: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_4_user_define_music_sheet_2_duration: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_4_user_define_music_sheet_2_strength: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_4_echo_instrument: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_4_echo_volume: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_4_name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_4_color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_4_type: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_4_align: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_5_music_sheet_type: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_5_user_define_instrument_0: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_5_user_define_instrument_1: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_5_user_define_instrument_2: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_5_user_define_instrument_3: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_5_user_define_instrument_4: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_5_user_define_instrument_5: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_5_user_define_instrument_6: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_5_user_define_instrument_7: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_5_user_define_volume: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_5_user_define_align_point: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_5_user_define_music_sheet_length: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_5_user_define_music_sheet_0_instrument_index: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_5_user_define_music_sheet_0_pitch: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_5_user_define_music_sheet_0_start: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_5_user_define_music_sheet_0_duration: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_5_user_define_music_sheet_0_strength: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_5_user_define_music_sheet_1_instrument_index: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_5_user_define_music_sheet_1_pitch: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_5_user_define_music_sheet_1_start: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_5_user_define_music_sheet_1_duration: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_5_user_define_music_sheet_1_strength: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_5_user_define_music_sheet_2_instrument_index: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_5_user_define_music_sheet_2_pitch: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_5_user_define_music_sheet_2_start: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_5_user_define_music_sheet_2_duration: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_5_user_define_music_sheet_2_strength: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_5_echo_instrument: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_5_echo_volume: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_5_name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_5_color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_5_type: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_5_align: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_6_music_sheet_type: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_6_user_define_instrument_0: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_6_user_define_instrument_1: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_6_user_define_instrument_2: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_6_user_define_instrument_3: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_6_user_define_instrument_4: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_6_user_define_instrument_5: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_6_user_define_instrument_6: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_6_user_define_instrument_7: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_6_user_define_volume: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_6_user_define_align_point: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_6_user_define_music_sheet_length: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_6_user_define_music_sheet_0_instrument_index: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_6_user_define_music_sheet_0_pitch: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_6_user_define_music_sheet_0_start: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_6_user_define_music_sheet_0_duration: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_6_user_define_music_sheet_0_strength: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_6_user_define_music_sheet_1_instrument_index: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_6_user_define_music_sheet_1_pitch: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_6_user_define_music_sheet_1_start: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_6_user_define_music_sheet_1_duration: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_6_user_define_music_sheet_1_strength: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_6_user_define_music_sheet_2_instrument_index: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_6_user_define_music_sheet_2_pitch: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_6_user_define_music_sheet_2_start: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_6_user_define_music_sheet_2_duration: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_6_user_define_music_sheet_2_strength: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_6_user_define_music_sheet_3_instrument_index: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_6_user_define_music_sheet_3_pitch: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_6_user_define_music_sheet_3_start: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_6_user_define_music_sheet_3_duration: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_6_user_define_music_sheet_3_strength: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_6_echo_instrument: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_6_echo_volume: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_6_name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_6_color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_6_type: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_6_align: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_7_music_sheet_type: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_7_user_define_instrument_0: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_7_user_define_instrument_1: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_7_user_define_instrument_2: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_7_user_define_instrument_3: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_7_user_define_instrument_4: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_7_user_define_instrument_5: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_7_user_define_instrument_6: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_7_user_define_instrument_7: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_7_user_define_volume: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_7_user_define_align_point: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_7_user_define_music_sheet_length: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_7_user_define_music_sheet_0_instrument_index: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_7_user_define_music_sheet_0_pitch: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_7_user_define_music_sheet_0_start: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_7_user_define_music_sheet_0_duration: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_7_user_define_music_sheet_0_strength: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_7_echo_instrument: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_7_echo_volume: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_7_name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_7_color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_7_type: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_7_align: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_8_music_sheet_type: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_8_user_define_instrument_0: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_8_user_define_instrument_1: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_8_user_define_instrument_2: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_8_user_define_instrument_3: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_8_user_define_instrument_4: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_8_user_define_instrument_5: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_8_user_define_instrument_6: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_8_user_define_instrument_7: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_8_user_define_volume: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_8_user_define_align_point: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_8_user_define_music_sheet_length: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_8_user_define_music_sheet_0_instrument_index: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_8_user_define_music_sheet_0_pitch: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_8_user_define_music_sheet_0_start: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_8_user_define_music_sheet_0_duration: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_8_user_define_music_sheet_0_strength: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_8_user_define_music_sheet_1_instrument_index: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_8_user_define_music_sheet_1_pitch: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_8_user_define_music_sheet_1_start: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_8_user_define_music_sheet_1_duration: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_8_user_define_music_sheet_1_strength: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_8_user_define_music_sheet_2_instrument_index: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_8_user_define_music_sheet_2_pitch: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_8_user_define_music_sheet_2_start: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_8_user_define_music_sheet_2_duration: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_8_user_define_music_sheet_2_strength: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_8_user_define_music_sheet_3_instrument_index: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_8_user_define_music_sheet_3_pitch: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_8_user_define_music_sheet_3_start: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_8_user_define_music_sheet_3_duration: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_8_user_define_music_sheet_3_strength: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_8_user_define_music_sheet_4_instrument_index: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_8_user_define_music_sheet_4_pitch: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_8_user_define_music_sheet_4_start: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_8_user_define_music_sheet_4_duration: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_8_user_define_music_sheet_4_strength: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_8_user_define_music_sheet_5_instrument_index: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_8_user_define_music_sheet_5_pitch: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_8_user_define_music_sheet_5_start: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_8_user_define_music_sheet_5_duration: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_8_user_define_music_sheet_5_strength: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_8_user_define_music_sheet_6_instrument_index: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_8_user_define_music_sheet_6_pitch: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_8_user_define_music_sheet_6_start: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_8_user_define_music_sheet_6_duration: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_8_user_define_music_sheet_6_strength: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_8_echo_instrument: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_8_echo_volume: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_8_name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_8_color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_8_type: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_8_align: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_9_music_sheet_type: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_9_user_define_instrument_0: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_9_user_define_instrument_1: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_9_user_define_instrument_2: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_9_user_define_instrument_3: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_9_user_define_instrument_4: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_9_user_define_instrument_5: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_9_user_define_instrument_6: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_9_user_define_instrument_7: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_9_user_define_volume: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_9_user_define_align_point: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_9_user_define_music_sheet_length: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_9_user_define_music_sheet_0_instrument_index: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_9_user_define_music_sheet_0_pitch: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_9_user_define_music_sheet_0_start: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_9_user_define_music_sheet_0_duration: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_9_user_define_music_sheet_0_strength: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_9_user_define_music_sheet_1_instrument_index: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_9_user_define_music_sheet_1_pitch: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_9_user_define_music_sheet_1_start: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_9_user_define_music_sheet_1_duration: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_9_user_define_music_sheet_1_strength: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_9_user_define_music_sheet_2_instrument_index: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_9_user_define_music_sheet_2_pitch: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_9_user_define_music_sheet_2_start: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_9_user_define_music_sheet_2_duration: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_9_user_define_music_sheet_2_strength: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_9_user_define_music_sheet_3_instrument_index: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_9_user_define_music_sheet_3_pitch: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_9_user_define_music_sheet_3_start: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_9_user_define_music_sheet_3_duration: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_9_user_define_music_sheet_3_strength: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_9_user_define_music_sheet_4_instrument_index: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_9_user_define_music_sheet_4_pitch: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_9_user_define_music_sheet_4_start: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_9_user_define_music_sheet_4_duration: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_9_user_define_music_sheet_4_strength: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_9_user_define_music_sheet_5_instrument_index: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_9_user_define_music_sheet_5_pitch: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_9_user_define_music_sheet_5_start: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_9_user_define_music_sheet_5_duration: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_9_user_define_music_sheet_5_strength: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_9_user_define_music_sheet_6_instrument_index: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_9_user_define_music_sheet_6_pitch: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_9_user_define_music_sheet_6_start: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_9_user_define_music_sheet_6_duration: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_9_user_define_music_sheet_6_strength: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_9_user_define_music_sheet_7_instrument_index: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_9_user_define_music_sheet_7_pitch: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_9_user_define_music_sheet_7_start: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_9_user_define_music_sheet_7_duration: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_9_user_define_music_sheet_7_strength: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_9_echo_instrument: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_9_echo_volume: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_9_name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_9_color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_9_type: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_9_align: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_10_music_sheet_type: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_10_user_define_instrument_0: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_10_user_define_instrument_1: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_10_user_define_instrument_2: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_10_user_define_instrument_3: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_10_user_define_instrument_4: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_10_user_define_instrument_5: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_10_user_define_instrument_6: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_10_user_define_instrument_7: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_10_user_define_volume: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_10_user_define_align_point: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_10_user_define_music_sheet_length: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_10_user_define_music_sheet_0_instrument_index: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_10_user_define_music_sheet_0_pitch: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_10_user_define_music_sheet_0_start: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_10_user_define_music_sheet_0_duration: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_10_user_define_music_sheet_0_strength: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_10_user_define_music_sheet_1_instrument_index: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_10_user_define_music_sheet_1_pitch: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_10_user_define_music_sheet_1_start: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_10_user_define_music_sheet_1_duration: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_10_user_define_music_sheet_1_strength: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_10_user_define_music_sheet_2_instrument_index: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_10_user_define_music_sheet_2_pitch: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_10_user_define_music_sheet_2_start: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_10_user_define_music_sheet_2_duration: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_10_user_define_music_sheet_2_strength: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_10_user_define_music_sheet_3_instrument_index: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_10_user_define_music_sheet_3_pitch: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_10_user_define_music_sheet_3_start: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_10_user_define_music_sheet_3_duration: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_10_user_define_music_sheet_3_strength: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_10_user_define_music_sheet_4_instrument_index: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_10_user_define_music_sheet_4_pitch: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_10_user_define_music_sheet_4_start: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_10_user_define_music_sheet_4_duration: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_10_user_define_music_sheet_4_strength: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_10_user_define_music_sheet_5_instrument_index: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_10_user_define_music_sheet_5_pitch: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_10_user_define_music_sheet_5_start: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_10_user_define_music_sheet_5_duration: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_10_user_define_music_sheet_5_strength: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_10_user_define_music_sheet_6_instrument_index: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_10_user_define_music_sheet_6_pitch: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_10_user_define_music_sheet_6_start: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_10_user_define_music_sheet_6_duration: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_10_user_define_music_sheet_6_strength: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_10_user_define_music_sheet_7_instrument_index: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_10_user_define_music_sheet_7_pitch: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_10_user_define_music_sheet_7_start: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_10_user_define_music_sheet_7_duration: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_10_user_define_music_sheet_7_strength: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_10_user_define_music_sheet_8_instrument_index: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_10_user_define_music_sheet_8_pitch: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_10_user_define_music_sheet_8_start: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_10_user_define_music_sheet_8_duration: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_10_user_define_music_sheet_8_strength: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_10_echo_instrument: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_10_echo_volume: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_10_name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_10_color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_10_type: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_10_align: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_11_music_sheet_type: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_11_user_define_instrument_0: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_11_user_define_instrument_1: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_11_user_define_instrument_2: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_11_user_define_instrument_3: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_11_user_define_instrument_4: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_11_user_define_instrument_5: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_11_user_define_instrument_6: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_11_user_define_instrument_7: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_11_user_define_volume: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_11_user_define_align_point: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_11_user_define_music_sheet_length: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_11_user_define_music_sheet_0_instrument_index: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_11_user_define_music_sheet_0_pitch: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_11_user_define_music_sheet_0_start: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_11_user_define_music_sheet_0_duration: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_11_user_define_music_sheet_0_strength: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_11_echo_instrument: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_11_echo_volume: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_11_name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_11_color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_11_type: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_11_align: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_12_music_sheet_type: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_12_user_define_instrument_0: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_12_user_define_instrument_1: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_12_user_define_instrument_2: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_12_user_define_instrument_3: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_12_user_define_instrument_4: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_12_user_define_instrument_5: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_12_user_define_instrument_6: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_12_user_define_instrument_7: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_12_user_define_volume: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_12_user_define_align_point: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_12_user_define_music_sheet_length: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_12_user_define_music_sheet_0_instrument_index: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_12_user_define_music_sheet_0_pitch: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_12_user_define_music_sheet_0_start: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_12_user_define_music_sheet_0_duration: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_12_user_define_music_sheet_0_strength: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_12_echo_instrument: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_12_echo_volume: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_12_name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_12_color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_12_type: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_12_align: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_13_music_sheet_type: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_13_user_define_instrument_0: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_13_user_define_instrument_1: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_13_user_define_instrument_2: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_13_user_define_instrument_3: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_13_user_define_instrument_4: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_13_user_define_instrument_5: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_13_user_define_instrument_6: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_13_user_define_instrument_7: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_13_user_define_volume: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_13_user_define_align_point: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_13_user_define_music_sheet_length: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_13_user_define_music_sheet_0_instrument_index: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_13_user_define_music_sheet_0_pitch: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_13_user_define_music_sheet_0_start: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_13_user_define_music_sheet_0_duration: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_13_user_define_music_sheet_0_strength: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_13_user_define_music_sheet_1_instrument_index: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_13_user_define_music_sheet_1_pitch: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_13_user_define_music_sheet_1_start: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_13_user_define_music_sheet_1_duration: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_13_user_define_music_sheet_1_strength: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_13_user_define_music_sheet_2_instrument_index: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_13_user_define_music_sheet_2_pitch: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_13_user_define_music_sheet_2_start: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_13_user_define_music_sheet_2_duration: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_13_user_define_music_sheet_2_strength: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_13_user_define_music_sheet_3_instrument_index: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_13_user_define_music_sheet_3_pitch: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_13_user_define_music_sheet_3_start: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_13_user_define_music_sheet_3_duration: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_13_user_define_music_sheet_3_strength: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_13_user_define_music_sheet_4_instrument_index: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_13_user_define_music_sheet_4_pitch: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_13_user_define_music_sheet_4_start: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_13_user_define_music_sheet_4_duration: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_13_user_define_music_sheet_4_strength: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_13_user_define_music_sheet_5_instrument_index: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_13_user_define_music_sheet_5_pitch: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_13_user_define_music_sheet_5_start: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_13_user_define_music_sheet_5_duration: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_13_user_define_music_sheet_5_strength: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_13_echo_instrument: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_13_echo_volume: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_13_name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_13_color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_13_type: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musica_13_align: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class 大市唱自动谱曲:
    class Meta:
        name = "自动谱曲"

    自然段开始: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    高潮开始: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    句子对开始: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    整体势值: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    整体势值自动: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    句子结构最高点: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    应用句子开头特色: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    应用句子中间特色: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    应用句子结尾特色: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    句子音高音量对比开始: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    句子音高音量对比值: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    句子上下行对比开始: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    句子上下行对比值: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    句子音节数对比开始: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    句子音节数对比值: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    句子结尾音高高: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    节拍结束: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    前面的音节音高高: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    前面的音节音量大: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    第一个音节是爆破音较重或者送气清擦音较重: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    最后一个音节时值长: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    最后一个音节结束后停顿: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    节拍持续时长: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )


@dataclass
class 大市唱谱曲:
    class Meta:
        name = "谱曲"

    句子开头的节拍停顿: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    句子开头两次上行: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    句子最高的地方变慢突出: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    上行下行之间停顿: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    倒数第二个音节滑音: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    倒数第二个音节上滑音下滑音交替: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    倒数第二个音节变快: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    倒数第二个音节加重: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    最后一个节拍上行: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class 大市唱音量包络:
    class Meta:
        name = "音量包络"

    开始位置x: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    开始位置y: Optional[Union[float, int]] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    开始方向相对x: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    开始方向相对y: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    中间位置x: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    中间位置y: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    中间左方向相对x: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    中间左方向相对y: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    中间右方向相对x: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    中间右方向相对y: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    结束位置x: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    结束位置y: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    结束方向相对x: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    结束方向相对y: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class 大市唱右附属发音小段数组:
    class Meta:
        name = "右附属发音小段数组"

    开始音标: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    开始音标_非音节性的影响者: Optional[object] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    开始音标_非音节性被影响的程度: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    𝓅清擦音最前面时域爆破: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    开始辅音音标: Optional[object] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    结束音标: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    结束音标_非音节性的影响者: Optional[object] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    结束音标_非音节性被影响的程度: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    持续时间: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    开始控制点时间: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    开始控制点频率: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    结束控制点时间: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    结束控制点频率: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    类型: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    继续: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    待续: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    结束音符是爆破音不参与参数渐变: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    开始音符是爆破音不参与参数渐变: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    清擦音实际长度: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    用于过度时使能: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    用于过度时本音节的时间: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    浊辅音前声带音实际长度: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    音量包络: Optional[大市唱音量包络] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class 大市唱后面的音节过度发音小段:
    class Meta:
        name = "后面的音节过度发音小段"

    开始音标: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    开始音标_非音节性的影响者: Optional[object] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    开始音标_非音节性被影响的程度: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    清擦音最前面时域爆破: Optional[float] = field(
        default=None,
        metadata={
            "name": "𝓅清擦音最前面时域爆破",
            "type": "Element",
            "required": True,
        },
    )
    开始辅音音标: Optional[object] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    结束音标: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    结束音标_非音节性的影响者: Optional[object] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    结束音标_非音节性被影响的程度: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    持续时间: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    开始控制点时间: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    开始控制点频率: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    结束控制点时间: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    结束控制点频率: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    类型: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    继续: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    待续: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    结束音符是爆破音不参与参数渐变: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    开始音符是爆破音不参与参数渐变: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    清擦音实际长度: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    用于过度时使能: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    用于过度时本音节的时间: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    浊辅音前声带音实际长度: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    音量包络: Optional[大市唱音量包络] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class 大市唱振幅变化:
    class Meta:
        name = "振幅变化"

    最小值: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    最大值: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    控制点数组: list[大市唱控制点数组] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )


@dataclass
class 大市唱振幅变化速度:
    class Meta:
        name = "振幅变化速度"

    最小值: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    最大值: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    控制点数组: list[大市唱控制点数组] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )


@dataclass
class 大市唱核心发音小段数组:
    class Meta:
        name = "核心发音小段数组"

    开始音标: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    开始音标_非音节性的影响者: Optional[object] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    开始音标_非音节性被影响的程度: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    清擦音最前面时域爆破: Optional[float] = field(
        default=None,
        metadata={
            "name": "𝓅清擦音最前面时域爆破",
            "type": "Element",
            "required": True,
        },
    )
    开始辅音音标: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    结束音标: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    结束音标_非音节性的影响者: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    结束音标_非音节性被影响的程度: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    持续时间: Optional[Union[float, int]] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    开始控制点时间: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    开始控制点频率: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    结束控制点时间: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    结束控制点频率: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    类型: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    继续: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    待续: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    结束音符是爆破音不参与参数渐变: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    开始音符是爆破音不参与参数渐变: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    清擦音实际长度: Optional[Union[int, float]] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    用于过度时使能: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    用于过度时本音节的时间: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    浊辅音前声带音实际长度: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    音量包络: Optional[大市唱音量包络] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class 大市唱频率变化:
    class Meta:
        name = "频率变化"

    控制点数组: list[大市唱控制点数组] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )
    最小值: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    最大值: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    上下对称: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class 大市唱频率变化速度:
    class Meta:
        name = "频率变化速度"

    最小值: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    最大值: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    控制点数组: list[大市唱控制点数组] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )


@dataclass
class 大市唱发音详细参数:
    class Meta:
        name = "发音详细参数"

    左附属发音小段数组: list[object] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )
    核心发音小段数组: list[大市唱核心发音小段数组] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )
    右附属发音小段数组: list[大市唱右附属发音小段数组] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )
    后面的音节过度发音小段: Optional[大市唱后面的音节过度发音小段] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class 大市唱音色属性:
    振幅变化: Optional[大市唱滤波] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    振幅变化速度: Optional[大市唱滤波] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    振幅变化随机分布: Optional[大市唱滤波] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    频率变化: Optional[大市唱滤波] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    频率变化速度: Optional[大市唱滤波] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    频率变化随机分布: Optional[大市唱滤波] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )


@dataclass
class 大市唱音色:
    class Meta:
        name = "音色"

    签名: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    类型: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    名称: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    颜色: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    身高: Optional[Union[float, int]] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    身高自动: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    滤波: Optional[大市唱滤波] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    滤波跟随频率: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    保留一倍频: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    一倍频振幅: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    共振峰宽度: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    高阶共振峰频谱位置: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    音色: Optional[大市唱音色属性] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    振幅变化: Optional[大市唱振幅变化] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    振幅变化速度: Optional[大市唱振幅变化速度] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    频率变化: Optional[大市唱频率变化] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    频率变化速度: Optional[大市唱频率变化速度] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    数据: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )


@dataclass
class 大市唱音节发音:
    class Meta:
        name = "音节发音"

    休止符: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    后面连音数量: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    左附属辅音: Optional[object] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    左核心辅音: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    核心元音: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    右核心辅音: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    右附属辅音: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    原生表音法的音节: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    音符显示: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    辅助显示: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    原文: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    分身: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    原文重复序号: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    句子中的位置: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    词的结束: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    发音详细参数: Optional[大市唱发音详细参数] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    右附属辅音可以借出: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    右附属辅音已经借出: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    右附属辅音可以去掉: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    右附属辅音已经去掉: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    核心左辅音可以借入: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    核心左辅音是借入的: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    核心左辅音可以借入的字符: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    左附属辅音可以去掉: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    左附属辅音已经去掉: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class 大市唱音符:
    class Meta:
        name = "音符"

    音高: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    时长: Optional[Union[float, int]] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    左侧过度时长: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    右侧过度时长: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    左侧吐字自动: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    左侧吐字延迟开始: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    左侧吐字建立耗时: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    右侧吐字自动: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    右侧吐字消失耗时: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    右侧吐字提前结束: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    连音: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    编曲修饰: list[object] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )
    自动谱曲: Optional[大市唱自动谱曲] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    音节发音: Optional[大市唱音节发音] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class 大市唱声乐曲:
    class Meta:
        name = "声乐曲"

    角色: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    副角色1: Optional[object] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    副角色2: Optional[object] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    乐器: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    副乐器1: Optional[object] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    副乐器2: Optional[object] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    自动谱曲: Optional[大市唱自动谱曲] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    语种: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    音符: list[大市唱音符] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )
    调号自动: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    调号: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    每分钟拍数: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    说唱: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    节拍配置名称: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    纯音乐: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    纯朗读: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    声乐曲音量: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    声乐曲清擦相对音量: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    编曲修饰音量: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    打节拍旋律音量: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    打节拍鼓音量: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    最后编辑时间: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    技巧: list[大市唱技巧] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )
    声乐清擦: list[object] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )
    声乐声带: list[object] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )
    副声乐声带1: list[object] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )
    副声乐声带2: list[object] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )
    编曲修饰: list[object] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )
    打节拍旋律: list[object] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )
    打节拍鼓: list[object] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )


@dataclass
class 大市唱文件格式:
    文件签名: Optional[str] = field(
        default="dscm",
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    主版本号: Optional[int] = field(
        default=1,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    副版本号: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    歌曲名称: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    文件名: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    作者: Optional[str] = field(
        default="赵磊",
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    组织: Optional[str] = field(
        default="没有组织是个人",
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    说明: Optional[str] = field(
        default="这家伙很懒，什么都没留下",
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    采样频率: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    正在编辑的行的索引: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    声乐曲: list[大市唱声乐曲] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )
    音色: list[大市唱音色] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )
    打节拍: list[大市唱打节拍] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )
    编曲: Optional[大市唱编曲] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    字典: list[大市唱字典] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    谱曲: Optional[大市唱谱曲] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )


if __name__ == "__main__":
    import pathlib

    from xsdata.formats.dataclass.parsers.config import ParserConfig
    from xsdata.formats.dataclass.parsers.json import JsonParser

    dsc_path = pathlib.Path("test.dsc")
    JsonParser(config=ParserConfig(fail_on_unknown_properties=False)).from_bytes(
        dsc_path.read_bytes(), 大市唱文件格式
    )
