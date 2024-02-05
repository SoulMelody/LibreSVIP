import pathlib
import subprocess

if __name__ == "__main__":
    subprocess.call(
        [
            "pyside6-rcc",
            "-g",
            "python",
            "-o",
            "../libresvip/gui/resources_rc.py",
            "../libresvip/gui/resources.qrc",
        ]
    )
    resource_file = pathlib.Path("../libresvip/gui/resources_rc.py")
    resource_content = resource_file.read_text(encoding="utf-8")
    resource_content = resource_content.strip().rpartition("\n")[0] + "\n"
    resource_content = resource_content.replace(
        "def qInitResources():", "def init_resources() -> None:"
    )
    resource_content = resource_content.replace(
        "def qCleanupResources():", "def cleanup_resources() -> None:"
    )
    resource_file.write_text(resource_content, encoding="utf-8")
