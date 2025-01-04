import argparse
import pathlib
import subprocess
import sys

from loguru import logger
from pip._vendor.packaging.requirements import InvalidRequirement, Requirement


def install_mobile_requirements(platform: str, arch: str) -> None:
    cwd = pathlib.Path()

    python_version = "3.12"
    wheels_dir = cwd / f"build/site-packages/{arch}"
    if not wheels_dir.exists():
        wheels_dir.mkdir(parents=True, exist_ok=True)
    common_args = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "--no-deps",
        "--target",
        str(wheels_dir),
        "--upgrade",
        "--no-compile",
    ]

    native_packages = [
        "cffi",
        "lxml",
        "markupsafe",
        "protobuf",
        "pycryptodomex",
        "pydantic-core",
        "pyyaml",
        "regex",
        "ruamel-yaml-clib",
        "zstandard",
    ]

    requirements_path = cwd / "requirements-android.txt"
    requirements = requirements_path.read_text().splitlines()
    project_wheel = next((cwd / "../dist/").glob("*.whl"))
    requirements.insert(0, f"libresvip @ {project_wheel.resolve()!s}")
    for requirement_str in requirements:
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
            logger.info(f"Installing {requirement.name}...")
            if requirement.name in native_packages:
                if requirement.name == "pydantic-core":
                    requirement_str = f"{requirement.name}{requirement.specifier}"
                else:
                    requirement_str = requirement.name
                subprocess.check_call(
                    [
                        *common_args,
                        requirement_str,
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
            elif requirement.name == "pymediainfo":
                subprocess.check_call(
                    [
                        *common_args,
                        f"{requirement.name}{requirement.specifier}",
                        "--no-binary",
                        ":all:",
                    ]
                )
            else:
                if requirement.url:
                    requirement_str = requirement.url
                else:
                    requirement_str = f"{requirement.name}{requirement.specifier}"
                try:
                    subprocess.check_call(
                        [
                            *common_args,
                            requirement_str,
                            "--platform",
                            "none",
                            "--only-binary",
                            ":all:",
                        ]
                    )
                except subprocess.CalledProcessError:
                    subprocess.check_call(
                        [
                            *common_args,
                            requirement_str,
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
    parser.add_argument(
        "--arch",
        default="arm64-v8a",
    )
    args = parser.parse_args()
    install_mobile_requirements(args.platform, args.arch)
