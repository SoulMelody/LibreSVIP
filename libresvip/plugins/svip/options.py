from enum import Enum
from typing import Annotated

from pydantic import BaseSettings, Field


class BinarySvipVersion(Enum):
    AUTO: Annotated[
        str,
        Field(
            title="自动选择",
            description="使用当前系统安装的 X Studio 所对应的工程文件版本。"
        )
    ] = 'auto'
    SVIP7_0_0: Annotated[
        str,
        Field(
            title="SVIP 7.0.0",
            description="使用 X Studio 2.0 对应的工程文件版本。"
        )
    ] = '7.0.0'
    SVIP6_0_0: Annotated[
        str,
        Field(
            title="SVIP 6.0.0",
            description="使用兼容 X Studio 1.8 的工程文件版本。"
        )
    ] = '6.0.0'
    COMPAT: Annotated[
        str,
        Field(
            title="最大只读兼容",
            description="""导出可使用任意版本 X Studio 打开的工程文件。
警告：使用此选项保存后，音量、气声、性别、力度参数将无法被 X Studio 识别（数据没有丢失）。
为了避免无法挽回的数据丢失，强烈建议不要使用 X Studio 修改和保存使用此选项导出的工程文件。若要重新将工程文件恢复至可安全编辑的状态，请选择保存为 SVIP 6.0.0 及以上版本。"""
        )
    ] = '0.0.0'


class InputOptions(BaseSettings):
    pass


class OutputOptions(BaseSettings):
    singer: str = Field(
        default='陈水若',
        title='无法匹配歌手时，使用此缺省歌手',
        description='请输入完整无误的歌手名字。若此选项指定的歌手不存在，将使用 X Studio 中设置的默认歌手。如果要指定歌手编号与名称的转换关系，或添加已拥有编号但未公开发行的歌手，请修改插件目录下的 SingerDict.json。'
    )
    tempo: int = Field(
        default=60,
        title='曲速过低或过高时，使用此曲速进行对齐',
        description='X Studio 支持的曲速范围为 20 ~ 300。曲速超出范围时，将会启用绝对时间轴以确保音符对齐。请尽量将此值设置为源工程文件中曲速的整数倍或整数分之一；只要在合理数值范围内，此选项的值不会影响对齐效果。',
    )
    version: BinarySvipVersion = Field(
        default=BinarySvipVersion.AUTO,
        title='指定生成的 .svip 文件版本',
        description='''此选项仅控制输出工程文件的头部版本信息。
        选择较旧的工程文件版本不会影响数据的完整性，但使用低版本的 X Studio 打开编辑并保存高版本工程文件时可能造成数据丢失。'''
    )
