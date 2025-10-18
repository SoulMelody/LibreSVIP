import pathlib
import subprocess

if __name__ == "__main__":
    py_dir = pathlib.Path("../libresvip/gui/modules")
    subprocess.call(
        [
            "pyside6-metaobjectdump",
            *(
                str(py_path)
                for py_path in py_dir.glob("*.py")
                if not py_path.name.startswith("frameless_window")
            ),
            "-o",
            "../libresvip/res/qml/components/plugins.json",
        ]
    )
    subprocess.call(
        [
            "pyside6-qmltyperegistrar",
            "--import-name=LibreSVIP",
            "--major-version=1",
            "--minor-version=0",
            "--generate-qmltypes",
            "../libresvip/res/qml/components/plugins.qmltypes",
            "../libresvip/res/qml/components/plugins.json",
        ]
    )
    pathlib.Path("../libresvip/res/qml/components/plugins.json").unlink()
