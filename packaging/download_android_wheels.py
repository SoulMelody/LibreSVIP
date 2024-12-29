import argparse
import os
import pathlib
import subprocess
import sys

from loguru import logger
from pip._vendor.packaging.requirements import InvalidRequirement, Requirement


def download_android_wheels(platform: str) -> None:
    cwd = pathlib.Path()

    python_version = "3.12"
    wheels_dir = cwd / "wheels"
    if not wheels_dir.exists():
        wheels_dir.mkdir()
    os.chdir(wheels_dir)

    native_packages = {
        "cffi": None,
        "lxml": None,
        "markupsafe": None,
        "protobuf": None,
        "pycryptodomex": None,
        "pydantic-core": "==2.23.3",
        "pyyaml": None,
        "regex": None,
        "ruamel-yaml-clib": None,
        "zstandard": None,
    }

    requirements_path = cwd / "../requirements-android.txt"
    for requirement_str in requirements_path.read_text().splitlines():
        try:
            requirement = Requirement(requirement_str)
        except InvalidRequirement:
            continue
        if (
            requirement.marker is None
            or requirement.marker.evaluate(
                environment={
                    "platform_system": "Android",
                    "python_version": python_version,
                    "python_full_version": python_version,
                    "sys_platform": "android",
                }
            )
            is True
        ):
            logger.info(f"Downloading {requirement.name}...")
            if requirement.name in native_packages:
                try:
                    subprocess.check_call(
                        [
                            sys.executable,
                            "-m",
                            "pip",
                            "download",
                            f"{requirement.name}{native_packages[requirement.name] or ''}",
                            "--no-deps",
                            "--platform",
                            platform,
                            "--only-binary",
                            ":all:",
                            "--python-version",
                            python_version,
                            "--index-url",
                            "https://pypi.flet.dev/",
                        ]
                    )
                    break
                except subprocess.CalledProcessError:
                    continue
            else:
                if requirement.name == "pymediainfo":
                    subprocess.check_call(
                        [
                            sys.executable,
                            "-m",
                            "pip",
                            "wheel",
                            f"{requirement.name}{requirement.specifier}",
                            "--no-deps",
                            "--no-binary",
                            ":all:",
                        ]
                    )
                else:
                    try:
                        subprocess.check_call(
                            [
                                sys.executable,
                                "-m",
                                "pip",
                                "download",
                                "pydantic==2.9.1"
                                if requirement.name == "pydantic"
                                else f"{requirement.name}{requirement.specifier}",
                                "--no-deps",
                                "--platform",
                                "none",
                                "--only-binary",
                                ":all:",
                            ]
                        )
                    except subprocess.CalledProcessError:
                        subprocess.check_call(
                            [
                                sys.executable,
                                "-m",
                                "pip",
                                "wheel",
                                f"{requirement.name}{requirement.specifier}",
                                "--no-deps",
                                "--no-binary",
                                ":all:",
                            ]
                        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--platform",
        default="android_24_arm64_v8a",
    )
    args = parser.parse_args()
    download_android_wheels(args.platform)
