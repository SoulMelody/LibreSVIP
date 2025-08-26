from enum import Enum
from typing import Annotated

from pydantic import Field, create_model

from libresvip.utils.translation import gettext_lazy as _


class AcepLyricsLanguage(Enum):
    _value_: Annotated[
        str,
        create_model(
            "AcepLyricsLanguage",
            __module__="libresvip.plugins.acep.enums",
            CHINESE=(str, Field(title=_("Chinese"))),
            JAPANESE=(str, Field(title=_("Japanese"))),
            ENGLISH=(str, Field(title=_("English"))),
            SPANISH=(str, Field(title=_("Spanish"))),
        ),
    ]
    CHINESE = "CHN"
    JAPANESE = "JPN"
    ENGLISH = "ENG"
    SPANISH = "SPA"
