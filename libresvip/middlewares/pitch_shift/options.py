from pydantic import BaseModel, Field


class ProcessOptions(BaseModel):
    key: int = Field(
        default=0,
        title="Key transition of pitch",
        description="Pitch shift in semitones.",
    )
