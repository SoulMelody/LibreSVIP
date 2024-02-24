import contextlib
import pathlib
import warnings
from typing import Optional, Union

from pymediainfo import ET, MediaInfo
from pymediainfo import Track as MediaInfoTrack

from libresvip.core.warning_types import UnknownWarning
from libresvip.utils.translation import gettext_lazy


def audio_track_info(
    file_path: Union[str, pathlib.Path], only_wav: bool = False
) -> Optional[MediaInfoTrack]:
    def filter_func(track: MediaInfoTrack) -> bool:
        return track.format == "PCM" if only_wav else (track.duration is not None)

    if MediaInfo.can_parse():
        try:
            with contextlib.suppress(ET.ParseError, RuntimeError, ValueError):
                media_info = MediaInfo.parse(file_path)
                if not len(media_info.video_tracks):
                    return next(
                        (track for track in media_info.audio_tracks if filter_func(track)),
                        None,
                    )
        except FileNotFoundError:
            _ = gettext_lazy
            warnings.warn(_("Audio file not found: ") + f"{file_path}", UnknownWarning)
    return None
