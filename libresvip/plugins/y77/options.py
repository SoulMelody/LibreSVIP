from pydantic import BaseModel, Field

from libresvip.core.constants import DEFAULT_BPM


class InputOptions(BaseModel):
    pass


class OutputOptions(BaseModel):
    tempo: float = Field(
        default=DEFAULT_BPM,
        title="Constant tempo",
        description="Use this tempo to reset time axis of projects with dynamic tempos",
    )
    track_index: int = Field(
        default=-1,
        title="Track index",
        description="Start from 0, -1 means auto select",
    )
