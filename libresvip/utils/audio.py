import contextlib
import pathlib
import platform
from typing import NewType

from pydantic import ValidationInfo

from libresvip.core.warning_types import show_warning
from libresvip.utils.translation import gettext_lazy as _


def audio_path_validator(path: str, info: ValidationInfo) -> str:
    audio_path = pathlib.Path(path)
    if not audio_path.is_absolute() and info.context is not None:
        project_path: pathlib.Path | None = info.context.get("path")
        if (project_path is not None) and not hasattr(project_path, "protocol"):
            audio_path = (project_path.parent / path).resolve()
            path = str(audio_path)
    return path


if platform.system() != "Emscripten":
    import xml.etree.ElementTree as ET

    from pymediainfo import MediaInfo
    from pymediainfo import Track as MediaInfoTrack

    def audio_track_info(
        file_path: str | pathlib.Path, only_wav: bool = False
    ) -> MediaInfoTrack | None:
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
                    media_info = MediaInfo.parse(file_path, library_file=library_name)
                    if not len(media_info.video_tracks):
                        return next(
                            (track for track in media_info.audio_tracks if filter_func(track)),
                            None,
                        )
            except FileNotFoundError:
                show_warning(_("Audio file not found: ") + f"{file_path}")
        return None
else:
    MediaInfoTrack = NewType("MediaInfoTrack", object)  # type: ignore[no-redef, misc]

    def audio_track_info(
        file_path: str | pathlib.Path, only_wav: bool = False
    ) -> MediaInfoTrack | None:  # not implemented yet
        return None
