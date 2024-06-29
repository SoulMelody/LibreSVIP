import contextlib
import contextvars
import gettext
import sys
from typing import Optional

singleton_translation: Optional[gettext.NullTranslations] = None
lazy_translation: contextvars.ContextVar[Optional[gettext.NullTranslations]] = (
    contextvars.ContextVar("translator")
)


def gettext_lazy(message: str) -> str:
    if not message:
        return message
    with contextlib.suppress(LookupError):
        if (translation := singleton_translation) is not None or (
            translation := lazy_translation.get(None)
        ) is not None:
            return translation.gettext(message)
    return gettext.gettext(message)


def pgettext_lazy(context: Optional[str], message: str) -> str:
    if context is None:
        frame = sys._getframe(1)
        context = frame.f_globals.get("__package__")
    if context is None:
        return gettext_lazy(message)
    if not message:
        return message
    with contextlib.suppress(LookupError):
        if (translation := singleton_translation) is not None or (
            translation := lazy_translation.get(None)
        ) is not None:
            return translation.pgettext(context, message)
    return gettext.pgettext(context, message)
