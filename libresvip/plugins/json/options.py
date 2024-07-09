from pydantic import BaseModel, Field

from libresvip.utils.translation import gettext_lazy as _


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
