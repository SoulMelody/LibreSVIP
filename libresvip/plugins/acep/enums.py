from enum import Enum
from typing import Annotated

from pydantic import Field

from libresvip.utils.translation import gettext_lazy as _


class AcepLyricsLanguage(Enum):
    CHINESE: Annotated[
        str,
        Field(
            title=_("Chinese"),
        ),
    ] = "CHN"
    JAPANESE: Annotated[
        str,
        Field(
            title=_("Japanese"),
        ),
    ] = "JPN"
    ENGLISH: Annotated[
        str,
        Field(
            title=_("English"),
        ),
    ] = "ENG"
    SPANISH: Annotated[
        str,
        Field(
            title=_("Spanish"),
        ),
    ] = "SPA"
