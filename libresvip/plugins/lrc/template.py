import pathlib

from jinja2 import Template

from .model import LrcFile

LRC_TEMPLATE = Template(
    """\
{% for info_tag in lrc_model.info_tags %}\
[{{ info_tag.key }}:{{ info_tag.value }}]
{% endfor %}\
{% for lyric_line in lrc_model.lyric_lines %}\
{% for time_tag in lyric_line.time_tags %}\
[{{ (time_tag.minute).__str__().rjust(2, '0') }}:\
{{ (time_tag.second).__str__().rjust(2, '0') }}.\
{{ (time_tag.percent_second).__str__().rjust(3, '0') }}]{% endfor %}\
{{ lyric_line.lyric }}\
{% endfor %}"""
)


def render_lrc(lrc_model: LrcFile, output_path: pathlib.Path) -> None:
    output_path.write_bytes(LRC_TEMPLATE.render(lrc_model=lrc_model).encode("utf-8"))
