import pathlib
import subprocess

import click
from packaging.requirements import InvalidRequirement, Requirement


@click.command()
@click.option(
    "--mingw-arch",
    type=click.Choice(["mingw-w64-x86_64", "mingw-w64-clang-x86_64", "mingw-w64-ucrt-x86_64"]),
    default="mingw-w64-x86_64",
)
def install_mingw_deps(mingw_arch: str) -> None:
    new_requirements = []
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
    cwd = pathlib.Path()
    subprocess.call(
        [
            "pacman",
            "-S",
            f"{mingw_arch}-libmediainfo",
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


if __name__ == "__main__":
    install_mingw_deps()
