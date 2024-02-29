import contextlib
import contextvars
import gettext
from typing import Optional

from libresvip.core.config import settings
from libresvip.core.constants import PACKAGE_NAME, res_dir

singleton_translation: Optional[gettext.NullTranslations] = None
lazy_translation: contextvars.ContextVar[Optional[gettext.NullTranslations]] = (
    contextvars.ContextVar("translator")
)


def gettext_lazy(message: str) -> str:
    with contextlib.suppress(LookupError):
        if (translation := singleton_translation) is not None or (
            translation := lazy_translation.get()
        ) is not None:
            return translation.gettext(message)
    return gettext.gettext(message)


# convertion functions copied from pydub
def get_translation(
    domain: str = PACKAGE_NAME, lang: Optional[str] = None
) -> gettext.NullTranslations:
    """Returns a gettext translation object.
    Adapted from https://github.com/Cimbali/pympress/blob/main/pympress/util.py

    This re-implements gettext's translation() and find() to allow using a python 3.9 Traversable as localedir

    Returns:
        :class:`~gettext.NullTranslations`: A gettext translation object with the strings for the domain loaded
    """
    localedir = res_dir / "locales"

    if lang is None:
        lang = settings.language.value

    if (file := localedir / lang / "LC_MESSAGES" / f"{domain}.mo").is_file():
        with file.open("rb") as fp:
            return gettext.GNUTranslations(fp)
    else:
        return gettext.NullTranslations()
