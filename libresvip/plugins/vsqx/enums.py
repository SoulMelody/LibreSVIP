import enum
from typing import Annotated

from pydantic import Field

from libresvip.utils.translation import gettext_lazy as _


class VsqxVersion(enum.IntEnum):
    VSQ3: Annotated[int, Field(title=_("VSQx 3"))] = 3
    VSQ4: Annotated[int, Field(title=_("VSQx 4"))] = 4


class VocaloidLanguage(enum.IntEnum):
    JAPANESE: Annotated[int, Field(title=_("日本語"))] = 0
    ENGLISH: Annotated[int, Field(title=_("English"))] = 1
    KOREAN: Annotated[int, Field(title=_("한국어"))] = 2
    SPANISH: Annotated[int, Field(title=_("Español"))] = 3
    SIMPLIFIED_CHINESE: Annotated[int, Field(title=_("简体中文"))] = 4
