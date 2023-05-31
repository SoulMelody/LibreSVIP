import contextlib
import shutil

with contextlib.suppress(ImportError, RuntimeError):
    if shutil.which("ffmpeg") is None:
        from libresvip.utils import download_and_setup_ffmpeg

        download_and_setup_ffmpeg()
