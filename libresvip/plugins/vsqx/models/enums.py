import enum
from typing import Annotated

from pydantic import Field, create_model

from libresvip.utils.translation import gettext_lazy as _


class VsqxVersion(enum.IntEnum):
    _value_: Annotated[
        int,
        create_model(
            "VsqxVersion",
            __module__="libresvip.plugins.vsqx.models.enums",
            VSQ3=(int, Field(title=_("VSQx 3"))),
            VSQ4=(int, Field(title=_("VSQx 4"))),
        ),
    ]
    VSQ3 = 3
    VSQ4 = 4


class VocaloidLanguage(enum.IntEnum):
    _value_: Annotated[
        int,
        create_model(
            "VocaloidLanguage",
            __module__="libresvip.plugins.vsqx.models.enums",
            JAPANESE=(int, Field(title=_("日本語"))),
            ENGLISH=(int, Field(title=_("English"))),
            KOREAN=(int, Field(title=_("한국어"))),
            SPANISH=(int, Field(title=_("Español"))),
            SIMPLIFIED_CHINESE=(int, Field(title=_("简体中文"))),
        ),
    ]
    JAPANESE = 0
    ENGLISH = 1
    KOREAN = 2
    SPANISH = 3
    SIMPLIFIED_CHINESE = 4
