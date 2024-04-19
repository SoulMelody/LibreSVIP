from pydantic import BaseModel, Field


class ProcessOptions(BaseModel):
    lyric_replacement_preset_name: str = Field(
        default="default",
        title="Name of lyric replacement preset",
    )
