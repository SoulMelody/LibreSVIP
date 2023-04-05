from pydantic import BaseModel, Field


class InputOptions(BaseModel):
    pass


class OutputOptions(BaseModel):
    indented: bool = Field(
        default=False, title="生成带缩进格式的 JSON 文件", description="缩进格式便于阅读与修改，但会占据较大的文件体积。"
    )
