from pydantic import BaseModel, Field


class InputOptions(BaseModel):
    dict_name: str = Field(
        default="opencpop-extension", title="词典名称"
    )


class OutputOptions(InputOptions):
    split_threshold: float = Field(
        default=0, title="分段长度（秒）",
        description="此选项控制转换时的分段策略。当此选项值为负时，不进行分段；此选项值为 0 时，在所有音符间隔达到阈值处分段；此选项值为正时，可在分段的基础上控制每个分段的最小长度。设置合理的分段策略能够在合成时减少显存占用的同时最大化利用性能，并提升合成效果。"
    )
    min_interval: int = Field(
        default=400, title="分段音符间隔（毫秒）",
        description="此选项控制分段时的音符间隔阈值。建议不小于 300 毫秒。"
    )
    seed: int = Field(
        default=-1, title="随机种子",
        description="固定随机种子可以得到稳定可复现的合成效果。此选项设置非负值时生效。"
    )
    export_gender: bool = Field(
        default=False, title="导出性别参数",
    )
    indent: int = Field(
        default=2, title="JSON缩进空格数",
        description="为负时不进行格式化。"
    )
    track_index: int = Field(default=-1, title="音轨序号", description="从0开始，-1表示自动选择")

