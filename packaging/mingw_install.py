import os
import pathlib
import site
import subprocess

from pip._vendor.packaging.requirements import InvalidRequirement, Requirement


def install_mingw_deps() -> None:
    sys_site_packages_path = site.getsitepackages()[-1]
    mingw_arch = os.environ.get("MINGW_PACKAGE_PREFIX", "mingw-w64-ucrt-x86_64")
    msystem = os.environ.get("MSYSTEM", "UCRT64")
    subprocess.call(
        [
            "wget",
            "-N",
            f"https://mirrors.tuna.tsinghua.edu.cn/msys2/mingw/{msystem.lower()}/{mingw_arch}-qt6-base-6.6.2-2-any.pkg.tar.zst",
        ]
    )
    subprocess.call(
        [
            "wget",
            "-N",
            f"https://mirrors.tuna.tsinghua.edu.cn/msys2/mingw/{msystem.lower()}/{mingw_arch}-qt6-declarative-6.6.2-1-any.pkg.tar.zst",
        ]
    )
    subprocess.call(
        [
            "wget",
            "-N",
            f"https://mirrors.tuna.tsinghua.edu.cn/msys2/mingw/{msystem.lower()}/{mingw_arch}-shiboken6-6.6.2-3-any.pkg.tar.zst",
        ]
    )
    subprocess.call(
        [
            "wget",
            "-N",
            f"https://mirrors.tuna.tsinghua.edu.cn/msys2/mingw/{msystem.lower()}/{mingw_arch}-pyside6-6.6.2-3-any.pkg.tar.zst",
        ]
    )
    subprocess.call(
        [
            "pacman",
            "--noconfirm",
            "-U",
            f"{mingw_arch}-qt6-base-6.6.2-2-any.pkg.tar.zst",
            f"{mingw_arch}-qt6-declarative-6.6.2-1-any.pkg.tar.zst",
            f"{mingw_arch}-shiboken6-6.6.2-3-any.pkg.tar.zst",
            f"{mingw_arch}-pyside6-6.6.2-3-any.pkg.tar.zst",
        ]
    )
    subprocess.call(["pacman", "-Sy"])
    new_requirements = []
    mingw_native_packages = {
        "annotated-types": "python-annotated-types",
        "anyio": "python-anyio",
        "charset-normalizer": "python-charset-normalizer",
        "cx-freeze": "python-cx-freeze",
        "cx-logging": "python-cx-logging",
        "lief": "python-lief",
        "lxml": "python-lxml",
        "markupsafe": "python-markupsafe",
        "nuitka": "python-nuitka",
        "pydantic": "python-pydantic",
        "pydantic-core": "python-pydantic-core",
        "pyside6": None,
        "pyside6-addons": None,
        "pyside6-essentials": None,
        "pyyaml": "python-yaml",
        "regex": "python-regex",
        "ruamel-yaml": "python-ruamel-yaml",
        "ruamel-yaml-clib": "python-ruamel.yaml.clib",
        "shiboken6": None,
        "ujson": "python-ujson",
        "winsdk": "python-winsdk",
        "zstandard": "python-zstandard",
    }
    cwd = pathlib.Path()
    subprocess.call(
        [
            "pacman",
            "-S",
            f"{mingw_arch}-gettext",
            "--noconfirm",
        ]
    )
    subprocess.call(
        [
            "pacman",
            "-S",
            f"{mingw_arch}-libmediainfo",
            "--noconfirm",
            "--needed",
        ]
    )
    subprocess.call(
        [
            "pacman",
            "-S",
            f"{mingw_arch}-python-cffi",
            "--noconfirm",
        ]
    )
    requirements_path = cwd / "requirements.txt"
    for requirement_str in requirements_path.read_text().splitlines():
        try:
            requirement = Requirement(requirement_str)
        except InvalidRequirement:
            continue
        if (
            requirement.marker is None or requirement.marker.evaluate() is True
        ) and requirement.name not in [
            "libresvip",
        ]:
            if requirement.name in mingw_native_packages:
                if (mingw_native_package := mingw_native_packages[requirement.name]) is not None:
                    subprocess.call(
                        [
                            "pacman",
                            "-S",
                            f"{mingw_arch}-{mingw_native_package}",
                            "--noconfirm",
                            "--needed",
                        ]
                    )
            else:
                new_requirements.append(requirement_str)
    requirements_path.write_text("\n".join(new_requirements))
    subprocess.call(["pip", "install", "-r", "requirements.txt", "--no-deps"])
    subprocess.call(
        [
            "ln",
            "-s",
            f"/{msystem.lower()}/bin/libmediainfo-0.dll",
            f"{sys_site_packages_path}/pymediainfo",
        ]
    )


if __name__ == "__main__":
    install_mingw_deps()
