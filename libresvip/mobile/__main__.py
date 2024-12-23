from __future__ import annotations

import sys

import flet as ft
from loguru import logger

from libresvip.mobile.app import main


def unraisablehook(unraisable: sys.UnraisableHookArgs) -> None:
    if unraisable.exc_type is not RuntimeError:
        logger.exception(unraisable.exc_value)
    del unraisable


sys.unraisablehook = unraisablehook


if __name__ == "__main__":
    ft.app(main, name="LibreSVIP")
