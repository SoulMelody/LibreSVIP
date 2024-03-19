import pathlib

from jinja2 import Template

from .model import NNProject

NN_TEMPLATE = Template(
    """\
{{ nn_project.info_line.tempo }} {{ nn_project.info_line.time_signature.numerator }} {{ nn_project.info_line.time_signature.denominator }} {{ nn_project.info_line.bar_count }} {{ nn_project.info_line.version }} {{ nn_project.info_line.unknown }} 0 0 0 0
{{ nn_project.note_count }}
{% for note in nn_project.notes %}\
 {{ note.lyric }} {{ note.pronunciation }} {{ note.start }} {{ note.duration }} {{ note.key }} {{ note.cle }} {{ note.vel }} {{ note.por }} {{ note.vibrato_length }} {{ note.vibrato_depth }} {{ note.vibrato_rate }} {{ note.dynamics.point_count }},{{ note.dynamics.points|join(',') }} {{ note.pitch.point_count }},{{ note.pitch.points|join(',') }} {{ note.pitch_bend_sensitivity }}
{% endfor %}\
"""
)


def render_nn(nn_project: NNProject, output_path: pathlib.Path) -> None:
    output_path.write_bytes(NN_TEMPLATE.render(nn_project=nn_project).encode("utf-8"))
