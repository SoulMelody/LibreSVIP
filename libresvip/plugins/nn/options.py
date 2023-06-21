from pydantic import BaseModel, Field


class InputOptions(BaseModel):
    pass


class OutputOptions(BaseModel):
    track_index: int = Field(
        default=-1,
        title="Track index",
        description="Start from 0, -1 means auto select",
    )
    version: int = Field(
        default=19,
        title="Version",
        description="Version of NIAONiao project file",
    )
