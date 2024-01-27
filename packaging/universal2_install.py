import contextlib
import pathlib

import pip
from delocate.fuse import fuse_wheels
from packaging.requirements import InvalidRequirement, Requirement

if __name__ == "__main__":
    # reference: https://github.com/python-pillow/Pillow/pull/6912/
    macos_single_platforms = ["macosx_10_10_x86_64", "macosx_11_0_arm64"]
    macos_universal_platform = "macosx_12_0_universal2"
    no_universal2_packages = [
        "pydantic-core",
        "ujson",
        "zstandard",
    ]
    cwd = pathlib.Path()
    requirements_path = cwd / "requirements.txt"
    new_requirements = []
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
                for macos_platform in macos_single_platforms:
                    requirement.specifier
                    pip.main(
                        [
                            "download",
                            f"{requirement.name}{requirement.specifier}",
                            "--platform",
                            macos_platform,
                            "--no-deps",
                            "--only-binary",
                            ":all:",
                        ]
                    )
                universal2_wheel_name = f"{normalized_name}-universal2.whl"
                single_platform_wheels = [
                    str(whl_path) for whl_path in cwd.glob(f"{normalized_name}*.whl")
                ]
                print(single_platform_wheels)  # noqa: T201
                with contextlib.suppress(FileNotFoundError):
                    fuse_wheels(
                        *single_platform_wheels,
                        universal2_wheel_name,
                    )
                    pip.main("install", universal2_wheel_name, "--no-deps")
            else:
                pip.main(
                    [
                        "install",
                        f"{requirement.name}{requirement.specifier}",
                        "--no-deps",
                        "--platform",
                        macos_universal_platform,
                        "--only-binary",
                        ":all:",
                    ]
                )
