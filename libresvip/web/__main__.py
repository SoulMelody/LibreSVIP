import pathlib
import runpy


def main():
    runpy.run_path(pathlib.Path(__file__).parent / "pages.py", run_name="__main__")


if __name__ == "__main__":
    runpy.run_module("libresvip.web.pages", run_name="__main__")
