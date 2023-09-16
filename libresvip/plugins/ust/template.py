import pathlib

from jinja2 import Template

from .model import UTAUProject

UST_TEMPLATE = Template(
    """\
[#VERSION]
UST Version={{ ust_project.ust_version[0] }}{% if ust_project.charset %}
Charset={{ ust_project.charset }}{% endif %}
[#SETTING]{% if ust_project.tempo | length > 0 %}
Tempo={{ ust_project.tempo[0] }}{% endif %}{% if ust_project.track_count | length > 0 %}
Tracks={{ ust_project.track_count[0] }}{% endif %}{% if ust_project.project_name | length > 0 %}
Project={{ ust_project.project_name[0] }}{% endif %}{% if ust_project.voice_dir | length > 0 %}
VoiceDir={{ ust_project.voice_dir[0] }}{% endif %}{% if ust_project.out_file | length > 0 %}
OutFile={{ ust_project.out_file[0] }}{% endif %}{% if ust_project.cache_dir | length > 0 %}
CacheDir={{ ust_project.cache_dir[0] }}{% endif %}{% if ust_project.tool1 | length > 0 %}
Tool1={{ ust_project.tool1[0] }}{% endif %}{% if ust_project.tool2 | length > 0 %}
Tool2={{ ust_project.tool2[0] }}{% endif %}{% if ust_project.pitch_mode2 | length > 0 %}
Mode2={{ ust_project.pitch_mode2[0] | round }}{% endif %}{% if ust_project.autoren | length > 0 %}
Autoren={{ ust_project.autoren[0] }}{% endif %}{% if ust_project.flags | length > 0 %}
Flags={{ ust_project.flags[0] }}{% endif %}{% if ust_project.track %}{% for note in ust_project.track[0].notes %}
[#{{ note.note_type }}]
Length={{ note.length[0] }}
Lyric={{ note.lyric[0] }}
NoteNum={{ note.note_num[0] }}{% if note.pre_utterance|length > 0 %}
PreUtterance={{ note.pre_utterance[0] | round(2) }}{% endif %}{% if note.voice_overlap|length > 0 %}
VoiceOverlap={{ note.voice_overlap[0] | round(2) }}{% endif %}{% if note.intensity|length > 0 %}
Intensity={{ note.intensity[0] | round(4) }}{% endif %}{% if note.modulation|length > 0 %}
Modulation={{ note.modulation[0] }}{% endif %}{% if note.start_point|length > 0 %}
StartPoint={{ note.start_point[0] | round(2) }}{% endif %}{% if note.envelope|length > 0 %}
Envelope={{ note.envelope.p1 }},{{ note.envelope.p2 }},{{ note.envelope.p3 }},{{ note.envelope.v1 }},{{ note.envelope.v2 }},{{ note.envelope.v3 }},{{ note.envelope.v4 }}\
{% if note.envelope.v5 %}\
,%,{{ note.envelope.p4 }},{{ note.envelope.p5 }},{{ note.envelope.v5 }}{% elif note.envelope.p5 %}\
,%,{{ note.envelope.p4 }},{{ note.envelope.p5 }}{% elif note.envelope.p4 %}\
,,{{ note.envelope.p4 }}{% endif %}{% endif %}{% if note.tempo|length > 0 %}
Tempo={{ note.tempo[0] }}{% endif %}{% if note.velocity|length > 0 %}
Velocity={{ note.velocity[0] | round(2) }}{% endif %}{% if note.label|length > 0 %}
Label={{ note.label[0] }}{% endif %}{% if note.flags|length > 0 %}
Flags={{ note.flags[0] }}{% endif %}{% if note.pitchbend_type|length > 0 %}
PBType={{ note.pitchbend_type[0] }}{% endif %}{% if note.pitchbend_start|length > 0 %}
PBStart={{ note.pitchbend_start[0] }}{% endif %}{% if note.pitch_bend_points|length > 0 %}
PitchBend={{ note.pitch_bend_points|join(',') }}{% endif %}{% if note.pbs|length > 0 %}
PBS={{ note.pbs | join(';') }}{% endif %}{% if note.pbw|length > 0 %}
PBW={{ note.pbw | join(',') }}{% endif %}{% if note.pby|length > 0 %}
PBY={{ note.pby | join(',') }}{% endif %}{% if note.pbm|length > 0 %}
PBM={{ note.pbm | join(',') }}{% endif %}{% if note.vbr|length > 0 %}
VBR={{ note.vbr | join(',') }}{% endif %}{% endfor %}
[#TRACKEND]{% endif %}
"""
)


def render_ust(
    ust_project: UTAUProject, output_path: pathlib.Path, encoding: str = "utf-8"
):
    output_path.write_text(
        UST_TEMPLATE.render(ust_project=ust_project), encoding=encoding
    )
