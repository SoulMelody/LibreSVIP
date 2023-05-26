import contextlib

with contextlib.suppress(ImportError, RuntimeError):
    import os
    import sys

    from imageio_ffmpeg import get_ffmpeg_exe

    sys.path.append(os.path.dirname(get_ffmpeg_exe()))
