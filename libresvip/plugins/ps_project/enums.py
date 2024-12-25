# mypy: disable-error-code="misc"
from enum import Enum
from typing import Annotated

from pydantic import Field

from libresvip.utils.translation import gettext_lazy as _


class PocketSingerLyricsLanguage(Enum):
    CHINESE: Annotated[
        str,
        Field(
            title=_("Chinese"),
        ),
    ] = "ch"
    JAPANESE: Annotated[
        str,
        Field(
            title=_("Japanese"),
        ),
    ] = "jp"
    ENGLISH: Annotated[
        str,
        Field(
            title=_("English"),
        ),
    ] = "en"
