from __future__ import annotations

import argparse
import os
import secrets
import sys

import flet as ft
from loguru import logger

from libresvip.core.config import settings
from libresvip.core.constants import app_dir
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
        from fastapi import FastAPI
        from fastapi.responses import FileResponse

        secrets_path = app_dir.user_config_path / "secrets.txt"
        if not secrets_path.exists():
            secrets_path.parent.mkdir(parents=True, exist_ok=True)
            secrets_path.write_text(secrets.token_urlsafe(32))
        os.environ["FLET_SECRET_KEY"] = secrets_path.read_text()
        flet_app = flet_web.fastapi.app(main, upload_dir=str(settings.save_folder))
        app = FastAPI()

        @app.get("/download/{filename}")
        def download(filename: str) -> FileResponse:
            return FileResponse(settings.save_folder / filename, filename=filename)

        app.mount("/", flet_app)

        uvicorn.run(app, host=args.host, port=args.port)
    else:
        ft.app(main, name="LibreSVIP")
