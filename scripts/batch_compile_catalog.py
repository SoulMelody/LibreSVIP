import pathlib

from babel.messages import setuptools_frontend

if __name__ == "__main__":
    base_dir = pathlib.Path("../libresvip")
    for file_path in base_dir.rglob("**/*.po"):
        if file_path.parent.name == "LC_MESSAGES":
            continue
        cmdinst = setuptools_frontend.compile_catalog()
        cmdinst.initialize_options()
        cmdinst.domain = file_path.stem
        cmdinst.directory = str(file_path.parent / "locales")
        cmdinst.output_file = str(file_path.with_suffix(".mo"))
        cmdinst.finalize_options()
        cmdinst.run()
