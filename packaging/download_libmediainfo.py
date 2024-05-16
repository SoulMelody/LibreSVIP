import pathlib
import shutil
import site
import subprocess

if __name__ == "__main__":
    sys_site_packages_path = site.getsitepackages()[-1]
    libmediainfo_version = "24.04"
    subprocess.call(
        [
            "curl",
            "-L",
            f"https://mediaarea.net/download/binary/libmediainfo0/{libmediainfo_version}/MediaInfo_DLL_{libmediainfo_version}_Mac_x86_64+arm64.tar.bz2",
            "--output",
            "libmediainfo.tar.bz2",
        ]
    )
    shutil.unpack_archive("libmediainfo.tar.bz2", "libmediainfo", "bztar")
    shutil.move(
        "libmediainfo/MediaInfoLib/libmediainfo.0.dylib",
        pathlib.Path(sys_site_packages_path) / "pymediainfo",
    )
