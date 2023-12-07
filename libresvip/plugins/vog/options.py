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
    singer_name: str = Field(
        title="Singer name",
        description="Please enter the singer's English name.",
        default="Doaz",
    )
