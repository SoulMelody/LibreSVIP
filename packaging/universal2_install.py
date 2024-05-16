import contextlib
import pathlib
import shutil
import site
import subprocess
import sys

from delocate.fuse import fuse_wheels
from pip._vendor.packaging.requirements import InvalidRequirement, Requirement

if __name__ == "__main__":
    # reference: https://github.com/python-pillow/Pillow/pull/6912/
    python_version = f"cp{sys.version_info.major}{sys.version_info.minor}"
    sys_site_packages_path = site.getsitepackages()[-1]
    macos_single_platforms = ["macosx_10_12_x86_64", "macosx_11_0_arm64"]
    macos_universal_platform = "macosx_12_0_universal2"
    no_universal2_packages = [
        "cx-Freeze",
        "pydantic-core",
        "PyYAML",
        "ruamel-yaml-clib",
        "ujson",
        "zstandard",
    ]
    libmediainfo_version = "24.04"
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
        ) and requirement.name != "libresvip":
            if requirement.name in no_universal2_packages:
                normalized_name = requirement.name.replace("-", "_")
                package_version = str(requirement.specifier).lstrip("<>=")
                for macos_platform in macos_single_platforms:
                    subprocess.call(
                        [
                            "pip",
                            "download",
                            f"{requirement.name}{requirement.specifier}",
                            "--platform",
                            macos_platform,
                            "--no-deps",
                            "--only-binary",
                            ":all:",
                        ]
                    )
                universal2_wheel_name = f"{normalized_name}-{package_version}-{python_version}-{python_version}-{macos_universal_platform}.whl"
                downloaded_wheels = [
                    str(whl_path) for whl_path in cwd.glob(f"{normalized_name}*.whl")
                ]
                if len(downloaded_wheels) == 2:
                    with contextlib.suppress(FileNotFoundError):
                        fuse_wheels(
                            *downloaded_wheels,
                            universal2_wheel_name,
                        )
                        subprocess.call(
                            [
                                "pip",
                                "install",
                                universal2_wheel_name,
                                "--no-deps",
                                "--upgrade",
                                "--target",
                                str(tmp_dir),
                            ]
                        )
                        shutil.copytree(tmp_dir, sys_site_packages_path, dirs_exist_ok=True)
                        shutil.rmtree(tmp_dir)
                else:  # wheel count mismatch, build from source
                    subprocess.call(
                        [
                            "pip",
                            "install",
                            f"{requirement.name}{requirement.specifier}",
                            "--no-deps",
                            "--upgrade",
                            "--target",
                            str(tmp_dir),
                        ]
                    )
                    shutil.copytree(tmp_dir, sys_site_packages_path, dirs_exist_ok=True)
                    shutil.rmtree(tmp_dir)
            else:
                subprocess.call(
                    [
                        "pip",
                        "install",
                        f"{requirement.name}{requirement.specifier}",
                        "--no-deps",
                        "--upgrade",
                        "--platform",
                        macos_universal_platform,
                        "--target",
                        str(tmp_dir),
                    ]
                )
                if requirement.name == "pymediainfo":
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
                        "libmediainfo/MediaInfoLib/libmediainfo.0.dylib", tmp_dir / "pymediainfo"
                    )
                shutil.copytree(tmp_dir, sys_site_packages_path, dirs_exist_ok=True)
                shutil.rmtree(tmp_dir)
