from pydantic import Field

from libresvip.model.base import BaseModel


class InputOptions(BaseModel):
    encoding: str = Field(
        default="auto",
        title="Text encoding",
    )


class OutputOptions(BaseModel):
    track_index: int = Field(
        default=-1,
        title="Track index",
        description="Start from 0, -1 means automatic selection",
    )
    version: float = Field(
        default=1.2,
        title="Version",
        description="UST file version",
    )
    encoding: str = Field(
        default="Shift_JIS",
        title="Text encoding",
    )
