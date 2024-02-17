import pathlib
import shutil
import site
import subprocess
import sys

from packaging.requirements import InvalidRequirement, Requirement

if __name__ == "__main__":
    new_requirements = []
    python_version = f"cp{sys.version_info.major}{sys.version_info.minor}"
    sys_site_packages_path = site.getsitepackages()[-1]
    mingw_arch = "mingw-w64-x86_64"  # "mingw-w64-clang-x86_64"  "mingw-w64-ucrt-x86_64" "mingw-w64-clang-aarch64"
    mingw_native_packages = {
        "annotated-types": "python-annotated-types",
        "anyio": "python-anyio",
        "charset-normalizer": "python-charset-normalizer",
        "cx-Freeze": "python-cx-freeze",
        "cx-Logging": "python-cx-logging",
        "lief": "python-lief",
        "nuitka": "python-nuitka",
        "pydantic-core": "python-pydantic-core",
        "pyside6": "pyside6",
        "PySide6-Addons": None,
        "PySide6-Essentials": None,
        "PyYAML": "python-yaml",
        "regex": "python-regex",
        "shiboken6": "shiboken6",
        "ujson": "python-ujson",
        "winsdk": "python-winsdk",
        "zstandard": "python-zstandard",
    }
    libmediainfo_version = "24.01"
    cwd = pathlib.Path()
    requirements_path = cwd / "requirements.txt"
    tmp_dir = cwd / "temp"
    for requirement_str in requirements_path.read_text().splitlines():
        try:
            requirement = Requirement(requirement_str)
        except InvalidRequirement:
            continue
        if (
            requirement.marker is None or requirement.marker.evaluate() is True
        ) and requirement.name not in [
            "libresvip",
            "packaging",
            "pyinstaller",
            "pefile",
            "pyinstaller-hooks-contrib",
        ]:
            if requirement.name in mingw_native_packages:
                if (mingw_native_package := mingw_native_packages[requirement.name]) is not None:
                    subprocess.call(
                        [
                            "pacman",
                            "-S",
                            f"{mingw_arch}-{mingw_native_package}",
                            "--noconfirm",
                        ]
                    )
            else:
                new_requirements.append(requirement_str)
    requirements_path.write_text("\n".join(new_requirements))
    subprocess.call(["pip", "install", "-r", "requirements.txt", "--no-deps"])
    subprocess.check_call(
        [
            "curl",
            "-L",
            f"https://mediaarea.net/download/binary/libmediainfo0/{libmediainfo_version}/MediaInfo_DLL_{libmediainfo_version}_Windows_x64_WithoutInstaller.zip",
            "--output",
            "libmediainfo.zip",
        ]
    )
    shutil.unpack_archive("libmediainfo.zip", "libmediainfo", "zip")
    shutil.move("libmediainfo/MediaInfo.dll", sys_site_packages_path / "pymediainfo")
