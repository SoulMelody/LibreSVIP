import contextlib

with contextlib.suppress(ImportError, RuntimeError):
    from imageio_ffmpeg import get_ffmpeg_exe
    from pydub import AudioSegment

    AudioSegment.converter = get_ffmpeg_exe()
