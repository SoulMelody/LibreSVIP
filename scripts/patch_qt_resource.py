import pathlib
import subprocess

if __name__ == "__main__":
    subprocess.call(
        [
            "pyside6-qmlformat",
            "-i",
            *(str(qml_path) for qml_path in pathlib.Path("../libresvip/res/qml").rglob("**/*.qml")),
        ]
    )
    subprocess.call(
        [
            "pyside6-rcc",
            "-g",
            "python",
            "-o",
            "../libresvip/gui/__init__.py",
            "../libresvip/res/qml/resources.qrc",
        ]
    )
    resource_file = pathlib.Path("../libresvip/gui/__init__.py")
    resource_content = resource_file.read_text(encoding="utf-8")
    resource_content = resource_content.strip().rpartition("\n")[0] + "\n\ninit_resources()\n"
    resource_content = resource_content.replace(
        "def qInitResources():", "\ndef init_resources() -> None:"
    )
    resource_content = resource_content.replace(
        "def qCleanupResources():", "\ndef cleanup_resources() -> None:"
    )
    resource_file.write_text(resource_content, encoding="utf-8")
