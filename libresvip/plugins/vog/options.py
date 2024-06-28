from gettext import gettext as _

from pydantic import BaseModel, Field

from libresvip.model.option_mixins import StaticTempoMixin


class InputOptions(BaseModel):
    pass


class OutputOptions(StaticTempoMixin, BaseModel):
    singer_name: str = Field(
        title=_("Singer name"),
        description=_("Please enter the singer's English name."),
        default="Doaz",
    )
