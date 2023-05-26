from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field


class BinarySvipVersion(Enum):
    AUTO: Annotated[
        str, Field(title="Auto detect", description="使用当前系统安装的 X Studio 所对应的工程文件版本。")
    ] = "auto"
    SVIP7_0_0: Annotated[
        str, Field(title="SVIP 7.0.0", description="使用 X Studio 2.0 对应的工程文件版本。")
    ] = "7.0.0"
    SVIP6_0_0: Annotated[
        str, Field(title="SVIP 6.0.0", description="使用兼容 X Studio 1.8 的工程文件版本。")
    ] = "6.0.0"
    COMPAT: Annotated[
        str,
        Field(
            title="Max compatibility (read only)",
            description="""导出可使用任意版本 X Studio 打开的工程文件。
警告：使用此选项保存后，音量、气声、性别、力度参数将无法被 X Studio 识别（数据没有丢失）。
为了避免无法挽回的数据丢失，强烈建议不要使用 X Studio 修改和保存使用此选项导出的工程文件。若要重新将工程文件恢复至可安全编辑的状态，请选择保存为 SVIP 6.0.0 及以上版本。""",
        ),
    ] = "0.0.0"


class InputOptions(BaseModel):
    pass


class OutputOptions(BaseModel):
    singer: str = Field(
        default="陈水若",
        title="Default singer",
        description="Please enter the singer's name in Chinese. If the specified singer does not exist, the default singer set in X Studio will be used. If you want to specify the conversion relationship between singer ID and name, or add a singer that has an ID but has not been publicly released, please modify singers.json in the plugin directory.",
    )
    tempo: int = Field(
        default=60,
        title="Default tempo",
        description="The allowed range of tempo in X Studio is 20 ~ 300. When the tempo is out of range, the absolute timeline will be used to ensure the alignment of notes. Please set this value to an integer multiple or integer fraction of the tempo in the source project file as much as possible; as long as it is within a reasonable range, the value of this option will not affect the alignment effect.",
    )
    version: BinarySvipVersion = Field(
        default=BinarySvipVersion.AUTO,
        title="Specify the version of the generated .svip file",
        description="""This option only controls the header version information of the output project file.
Choosing an older project file version will not affect the integrity of the data, but using a lower version of X Studio to open, edit and save a higher version project file may cause data loss.""",
    )
