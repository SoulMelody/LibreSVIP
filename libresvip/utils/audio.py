import contextlib
import pathlib
import platform
from typing import Optional, Union

from pydantic import ValidationInfo

from libresvip.core.warning_types import show_warning
from libresvip.utils.translation import gettext_lazy as _


def audio_path_validator(path: str, info: ValidationInfo) -> str:
    audio_path = pathlib.Path(path)
    if not audio_path.is_absolute() and info.context is not None:
        project_path: Optional[pathlib.Path]
        if (project_path := info.context.get("path")) and not hasattr(project_path, "protocol"):
            audio_path = (project_path.parent / path).resolve()
            path = str(audio_path)
    return path


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
    import js
    from pyodide.ffi import run_sync
    from xsdata.formats.dataclass.parsers.config import ParserConfig
    from xsdata_pydantic.bindings import XmlParser

    from .mediainfo_wasm import MediaInfo
    from .mediainfo_wasm import Track as MediaInfoTrack

    if not hasattr(js, "MediaInfo"):
        js.importScripts(
            "https://fastly.jsdelivr.net/npm/mediainfo.js@latest/dist/umd/index.min.js"
        )

    def audio_track_info(
        file_path: Union[str, pathlib.Path], only_wav: bool = False
    ) -> Optional[MediaInfoTrack]:
        if isinstance(file_path, str):
            file_path = pathlib.Path(file_path)

        def filter_func(track: MediaInfoTrack) -> bool:
            return track.format == "PCM" if only_wav else (track.duration is not None)

        def read_chunk(size: int, offset: int) -> js.Uint8Array:
            chunk = content[offset : offset + size]
            js_buf = js.Uint8Array.new(len(chunk))
            js_buf.assign(chunk)
            return js_buf

        def locate_file(path: str, prefix: str) -> str:
            return "https://fastly.jsdelivr.net/npm/mediainfo.js@latest/dist/MediaInfoModule.wasm"

        async def parse_media_info() -> str:
            media_info = await MediaInfo.mediaInfoFactory(format="XML", locateFile=locate_file)
            result = await media_info.analyzeData(len(content), read_chunk)
            media_info.close()
            return result

        if hasattr(js, "MediaInfo"):
            if file_path.exists():
                with contextlib.suppress(RuntimeError, ValueError):
                    content = file_path.read_bytes()
                    xml_str = run_sync(parse_media_info())
                    media_info = XmlParser(
                        config=ParserConfig(fail_on_unknown_properties=False)
                    ).from_string(xml_str, MediaInfo)
                    if not len(media_info.video_tracks):
                        return next(
                            (track for track in media_info.audio_tracks if filter_func(track)),
                            None,
                        )
            else:
                show_warning(_("Audio file not found: ") + f"{file_path}")
        return None
