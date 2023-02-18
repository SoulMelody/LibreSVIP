import pathlib

from jinja2 import Template

from .model import NNProject

NN_TEMPLATE = Template(
    """\

"""
)


def render_nn(nn_project: NNProject, output_path: pathlib.Path):
    output_path.write_text(NN_TEMPLATE.render(nn_project=nn_project), encoding="utf-8")
