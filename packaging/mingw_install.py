import os
import pathlib
import shutil
import site
import subprocess

from pip._vendor.packaging.requirements import InvalidRequirement, Requirement


def install_mingw_deps() -> None:
    os.environ.setdefault("SETUPTOOLS_USE_DISTUTILS", "stdlib")
    sys_site_packages_path = site.getsitepackages()[-1]
    mingw_arch = os.environ.get("MINGW_PACKAGE_PREFIX", "mingw-w64-ucrt-x86_64")
    assert mingw_arch.endswith("64")
    msystem = os.environ.get("MSYSTEM", "UCRT64")
    pacman_available = shutil.which("pacman.exe") is not None
    msys2_requirements = [f"{mingw_arch}-python-pip", f"{mingw_arch}-python-uv"]

    def install_msys2_requirements(args: list[str]) -> None:
        nonlocal msys2_requirements
        if pacman_available:
            subprocess.check_call(args)
        else:
            msys2_requirements.append(args[2])

    if pacman_available:
        subprocess.call(["pacman", "-Sy"])
    new_requirements = []
    mingw_native_packages = {
        "annotated-types": "python-annotated-types",
        "anyio": "python-anyio",
        "charset-normalizer": "python-charset-normalizer",
        "cx-freeze": None,
        "cx-logging": None,
        "lief": None,
        "lxml": "python-lxml",
        "markupsafe": "python-markupsafe",
        "nuitka": "python-nuitka",
        "protobuf": "python-protobuf",
        "pydantic": "python-pydantic",
        "pydantic-core": "python-pydantic-core",
        "pyside6": "pyside6",
        "pyside6-addons": None,
        "pyside6-essentials": None,
        "pyyaml": "python-yaml",
        "regex": "python-regex",
        "ruamel-yaml": "python-ruamel-yaml",
        "ruamel-yaml-clib": "python-ruamel.yaml.clib",
        "shellingham": "python-shellingham",
        "shiboken6": None,
        "ujson": "python-ujson",
        "zstandard": "python-zstandard",
    }
    cwd = pathlib.Path()
    install_msys2_requirements(
        [
            "pacman",
            "-S",
            f"{mingw_arch}-gettext",
            "--noconfirm",
        ]
    )
    install_msys2_requirements(
        [
            "pacman",
            "-S",
            f"{mingw_arch}-libmediainfo",
            "--noconfirm",
            "--needed",
        ]
    )
    install_msys2_requirements(
        [
            "pacman",
            "-S",
            f"{mingw_arch}-python-cffi",
            "--noconfirm",
        ]
    )
    if "clang" in mingw_arch:
        install_msys2_requirements(
            [
                "pacman",
                "-S",
                f"{mingw_arch}-gcc-compat",
                "--noconfirm",
            ],
        )
    else:
        install_msys2_requirements(
            [
                "pacman",
                "-S",
                f"{mingw_arch}-gcc",
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
                    install_msys2_requirements(
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
    if pacman_available:
        subprocess.call(["uv", "pip", "install", "-r", "requirements.txt", "--no-deps", "--system"])
        subprocess.call(
            [
                "ln",
                "-s",
                f"/{msystem.lower()}/bin/libmediainfo-0.dll",
                f"{sys_site_packages_path}/pymediainfo",
            ]
        )
    else:
        (cwd / "install_msys2_requirements.sh").write_text(
            f"pacman -S {' '.join(msys2_requirements)} --noconfirm --needed"
        )


if __name__ == "__main__":
    install_mingw_deps()
