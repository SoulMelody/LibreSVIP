from pydantic import BaseModel, Field


class InputOptions(BaseModel):
    pass


class OutputOptions(BaseModel):
    singer_name: str = Field(
        title="Singer name",
        description="Please enter the singer's English name.",
        default="Doaz",
    )
