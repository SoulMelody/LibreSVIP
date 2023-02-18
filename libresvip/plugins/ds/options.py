from pydantic import BaseSettings, Field


class InputOptions(BaseSettings):
    dict_name: str = Field(
        default="opencpop-extension", title="词典名称"
    )


class OutputOptions(BaseSettings):
    pass
