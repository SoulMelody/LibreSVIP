from pydantic import BaseModel, Field


class InputOptions(BaseModel):
    pass


class OutputOptions(BaseModel):
    default_singer_name: str = Field(
        "嫣汐",
        title="Default Singer Name",
        description="The default singer name to use for all tracks",
    )
