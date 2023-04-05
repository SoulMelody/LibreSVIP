from pydantic import BaseModel, Field


class InputOptions(BaseModel):
    pass


class OutputOptions(BaseModel):
    track_index: int = Field(default=-1, title="音轨序号", description="从0开始，-1表示自动选择")
