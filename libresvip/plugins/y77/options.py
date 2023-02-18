from pydantic import BaseSettings, Field


class InputOptions(BaseSettings):
    pass


class OutputOptions(BaseSettings):
    track_index: int = Field(default=-1, title="音轨序号", description="从0开始，-1表示自动选择")
