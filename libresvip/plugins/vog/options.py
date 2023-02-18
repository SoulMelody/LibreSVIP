from pydantic import BaseSettings, Field


class InputOptions(BaseSettings):
    pass


class OutputOptions(BaseSettings):
    singer_name: str = Field(
        title="歌手",
        description="请输入完整无误的歌手英文名字。",
        default="Doaz"
    )
