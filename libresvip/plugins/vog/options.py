from pydantic import BaseModel, Field


class InputOptions(BaseModel):
    pass


class OutputOptions(BaseModel):
    singer_name: str = Field(
        title="歌手",
        description="请输入完整无误的歌手英文名字。",
        default="Doaz"
    )
