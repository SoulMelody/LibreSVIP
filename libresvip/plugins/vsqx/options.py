from pydantic import BaseModel, Field


class InputOptions(BaseModel):
    pass


class OutputOptions(BaseModel):
    pretty_xml: bool = Field(
        True, title="Pretty XML", description="Whether to output pretty XML"
    )
    default_comp_id: str = Field(
        "BETDB8W6KWZPYEB9",
        title="Default Comp ID",
        description="Default comp_id of voicebank",
    )
    default_singer_name: str = Field(
        "Tianyi_CHN",
        title="Default Singer Name",
        description="Default singer name of voicebank",
    )
