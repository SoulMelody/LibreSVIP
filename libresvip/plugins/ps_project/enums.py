from enum import Enum
from typing import Annotated

from pydantic import Field, create_model

from libresvip.utils.translation import gettext_lazy as _


class PocketSingerLyricsLanguage(Enum):
    _value_: Annotated[
        str,
        create_model(
            "PocketSingerLyricsLanguage",
            __module__="libresvip.plugins.ps_project.enums",
            CHINESE=(str, Field(title=_("Chinese"))),
            JAPANESE=(str, Field(title=_("Japanese"))),
            ENGLISH=(str, Field(title=_("English"))),
        ),
    ]
    CHINESE = "ch"
    JAPANESE = "jp"
    ENGLISH = "en"
