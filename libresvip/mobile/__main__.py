from __future__ import annotations

import argparse
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
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--host", type=str, default="127.0.0.1")
    arg_parser.add_argument("--port", type=int, default=8080)
    arg_parser.add_argument("--web", action="store_true", help="Run in web mode")
    args, argv = arg_parser.parse_known_args()
    if args.web:
        import flet_web.fastapi
        import uvicorn

        app = flet_web.fastapi.app(main, before_main=None)

        uvicorn.run(app, host=args.host, port=args.port)
    else:
        ft.run(main, name="LibreSVIP", no_cdn=True)
