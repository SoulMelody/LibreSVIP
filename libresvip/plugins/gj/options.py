from pydantic import BaseSettings, Field


class InputOptions(BaseSettings):
    pass


class OutputOptions(BaseSettings):
    down_sample: int = Field(
        default=32,
        title="音量参数平均采样间隔",
        description="单位为Tick。数值越大，编辑器越流畅；数值越小，音量参数越精确。"
    )
    singer: str = Field(
        default="扇宝",
        title="默认歌手",
    )
