from __future__ import annotations

import sys

from loguru import logger

from libresvip.web.pages import main


def unraisablehook(unraisable: sys.UnraisableHookArgs) -> None:
    if unraisable.exc_type is not KeyboardInterrupt:
        logger.exception(unraisable.exc_value)
    del unraisable


sys.unraisablehook = unraisablehook

if __name__ in {"__main__", "__mp_main__"}:
    main()
