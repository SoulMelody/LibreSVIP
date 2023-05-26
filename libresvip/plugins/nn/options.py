from pydantic import BaseModel, Field


class InputOptions(BaseModel):
    pass


class OutputOptions(BaseModel):
    track_index: int = Field(
        default=-1,
        title="Track index",
        description="Start from 0, -1 means auto select",
    )
