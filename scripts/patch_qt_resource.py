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
            "--binary",
            "-o",
            "../libresvip/res/resources.rcc",
            "../libresvip/res/qml/resources.qrc",
        ]
    )
