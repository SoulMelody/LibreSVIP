import typer
from babel.messages import setuptools_frontend

if __name__ == "__main__":
    cmdinst = setuptools_frontend.extract_messages()
    cmdinst.initialize_options()
    cmdinst.input_paths = [str(typer.__path__[0])]
    cmdinst.output_file = "../translations/typer.pot"
    cmdinst.no_location = True
    cmdinst.finalize_options()
    cmdinst.run()
