from gettext import gettext as _

from pydantic import BaseModel, Field


class InputOptions(BaseModel):
    pass


class OutputOptions(BaseModel):
    indented: bool = Field(
        default=False,
        title=_("Generate JSON file with indentation"),
        description=_(
            "The indented format is easier to read and modify, but it will take up a larger file size."
        ),
    )
