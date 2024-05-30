import contextlib
import pathlib
import platform
from typing import Any, Optional, Union

from libresvip.core.warning_types import show_warning
from libresvip.utils.translation import gettext_lazy as _

if platform.system() != "Emscripten":
    from pymediainfo import ET, MediaInfo
    from pymediainfo import Track as MediaInfoTrack

    def audio_track_info(
        file_path: Union[str, pathlib.Path], only_wav: bool = False
    ) -> Optional[MediaInfoTrack]:
        def filter_func(track: MediaInfoTrack) -> bool:
            return track.format == "PCM" if only_wav else (track.duration is not None)

        library_name = None
        if platform.system() == "Windows":
            python_compiler = platform.python_compiler()
            if python_compiler.startswith("GCC"):
                library_name = "libmediainfo-0.dll"

        if MediaInfo.can_parse(library_name):
            try:
                with contextlib.suppress(ET.ParseError, RuntimeError, ValueError):
                    media_info = MediaInfo.parse(file_path, library_name)
                    if not len(media_info.video_tracks):
                        return next(
                            (track for track in media_info.audio_tracks if filter_func(track)),
                            None,
                        )
            except FileNotFoundError:
                show_warning(_("Audio file not found: ") + f"{file_path}")
        return None
else:

    def audio_track_info(
        file_path: Union[str, pathlib.Path], only_wav: bool = False
    ) -> Optional[Any]:
        pass
