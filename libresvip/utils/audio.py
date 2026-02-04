import contextlib
import dataclasses
import pathlib
import platform

from pydantic import ValidationInfo

from libresvip.core.warning_types import show_warning
from libresvip.utils.translation import gettext_lazy as _


@dataclasses.dataclass
class SoundFileInfo:
    sample_rate: int
    channels: int
    format: str
    duration: float
    bit_depth: int | None = None


def audio_path_validator(path: str, info: ValidationInfo) -> str:
    audio_path = pathlib.Path(path)
    if not audio_path.is_absolute() and info.context is not None:
        project_path: pathlib.Path | None = info.context.get("path")
        if (project_path is not None) and not hasattr(project_path, "protocol"):
            audio_path = (project_path.parent / path).resolve()
            path = str(audio_path)
    return path


try:
    import xml.etree.ElementTree as ET

    from pymediainfo import MediaInfo
    from pymediainfo import Track as MediaInfoTrack

    def mediainfo_track2soundfile_info(track: MediaInfoTrack) -> SoundFileInfo:
        return SoundFileInfo(
            sample_rate=track.sampling_rate,
            channels=track.channel_s,
            bit_depth=track.bit_depth,
            format=track.format,
            duration=track.duration / 1000 if track.duration is not None else 0,
        )

    def audio_track_info(
        file_path: str | pathlib.Path, only_wav: bool = False
    ) -> SoundFileInfo | None:
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
                            (
                                mediainfo_track2soundfile_info(track)
                                for track in media_info.audio_tracks
                                if filter_func(track)
                            ),
                            None,
                        )
            except FileNotFoundError:
                show_warning(_("Invalid audio file: ") + f"{file_path}")
        return None
except ImportError:
    import re

    import soundfile as sf

    BIT_DEPTH_PATTERN = re.compile(r"(?:^|\n)\s+Bit width\s+:\s+(\d+)(?:\n|$)")

    def _soundfile_info2soundfile_info(info: sf._SoundFileInfo) -> SoundFileInfo:
        bit_depth_match = BIT_DEPTH_PATTERN.search(info.extra_info)
        return SoundFileInfo(
            sample_rate=info.samplerate,
            channels=info.channels,
            bit_depth=int(bit_depth_match.group(1)) if bit_depth_match is not None else None,
            format=info.format,
            duration=info.duration,
        )

    def audio_track_info(
        file_path: str | pathlib.Path, only_wav: bool = False
    ) -> SoundFileInfo | None:
        try:
            info = _soundfile_info2soundfile_info(sf.info(file_path))
        except sf.LibsndfileError:
            show_warning(_("Invalid audio file: ") + f"{file_path}")
            return None
        else:
            return info if not only_wav or info.format == "WAV" else None
