import pathlib

from libresvip.core.compat import jinja_env

from .model import LrcFile

jinja_env.add_template(
    "lrc",
    """\
{% for info_tag in lrc_model.info_tags %}\
[{{ info_tag.key }}:{{ info_tag.value }}]
{% endfor %}\
{% for lyric_line in lrc_model.lyric_lines %}\
{% for time_tag in lyric_line.time_tags %}\
[{{ time_tag }}]{% endfor %}\
{{ lyric_line.lyric }}\
{% endfor %}""",
)


def render_lrc(lrc_model: LrcFile, output_path: pathlib.Path) -> None:
    output_path.write_bytes(jinja_env.render_template("lrc", lrc_model=lrc_model).encode("utf-8"))
