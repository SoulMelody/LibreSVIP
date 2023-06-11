import pathlib

from jinja2 import Template

from .model import UTAUProject

UST_TEMPLATE = Template(
    """\
[#VERSION]
UST Version={{ ust_project.version_info.ust_version }}{% if ust_project.version_info.charset %}
Charset={{ ust_project.version_info.charset }}{% endif %}
[#SETTING]
Tempo={{ ust_project.tempo }}{% if ust_project.track_count %}
Tracks={{ ust_project.track_count }}{% endif %}{% if ust_project.project_name %}
Project={{ ust_project.project_name }}{% endif %}{% if ust_project.voice_dir %}
VoiceDir={{ ust_project.voice_dir }}{% endif %}{% if ust_project.out_file %}
OutFile={{ ust_project.out_file }}{% endif %}{% if ust_project.cache_dir %}
CacheDir={{ ust_project.cache_dir }}{% endif %}{% if ust_project.tool1 %}
Tool1={{ ust_project.tool1 }}{% endif %}{% if ust_project.tool2 %}
Tool2={{ ust_project.tool2 }}{% endif %}{% if ust_project.pitch_mode2 %}
Mode2={{ ust_project.pitch_mode2 }}{% endif %}{% if ust_project.autoren %}
Autoren={{ ust_project.autoren }}{% endif %}{% if ust_project.flags %}
Flags={{ ust_project.flags }}{% endif %}{% if ust_project.track %}{% for note in ust_project.track.notes %}
[#{{ note.note_type }}]
Length={{ note.length }}
Lyric={{ note.lyric }}
NoteNum={{ note.note_num }}{% if note.pre_utterance|length > 1 %}
PreUtterance={{ note.pre_utterance }}{% endif %}{% if note.voice_overlap|length > 1 %}
VoiceOverlap={{ note.voice_overlap }}{% endif %}{% if note.intensity|length > 1 %}
Intensity={{ note.intensity }}{% endif %}{% if note.modulation|length > 1 %}
Modulation={{ note.modulation }}{% endif %}{% if note.start_point|length > 1 %}
StartPoint={{ note.start_point }}{% endif %}{% if note.envelope|length > 1 %}
Envelope={{ note.envelope.p1 }},{{ note.envelope.p2 }},{{ note.envelope.p3 }},{{ note.envelope.v1 }},{{ note.envelope.v2 }},{{ note.envelope.v3 }},{{ note.envelope.v4 }}\
{% if note.envelope.v5 %}\
,%,{{ note.envelope.p4 }},{{ note.envelope.p5 }},{{ note.envelope.v5 }}{% elif note.envelope.p5 %}\
,%,{{ note.envelope.p4 }},{{ note.envelope.p5 }}{% elif note.envelope.p4 %}\
,,{{ note.envelope.p4 }}{% endif %}{% endif %}{% if note.tempo|length > 1 %}
Tempo={{ note.tempo }}{% endif %}{% if note.velocity|length > 1 %}
Velocity={{ note.velocity }}{% endif %}{% if note.label|length > 1 %}
Label={{ note.label }}{% endif %}{% if note.flags|length > 1 %}
Flags={{ note.flags }}{% endif %}{% if note.pitchbend_type|length > 1 %}
PBType={{ note.pitchbend_type }}{% endif %}{% if note.pitchbend_start|length > 1 %}
PBStart={{ note.pitchbend_start }}{% endif %}{% if note.pitch_bend_points|length > 1 %}
PitchBend={{ note.pitch_bend_points|join(',') }}{% endif %}{% if note.pbs|length > 1 %}
PBS={{ note.pbs | join(';') }}{% endif %}{% if note.pbw|length > 1 %}
PBW={{ note.pbw | join(',') }}{% endif %}{% if note.pby|length > 1 %}
PBY={{ note.pby | join(',') }}{% endif %}{% if note.pbm|length > 1 %}
PBM={{ note.pbm | join(',') }}{% endif %}{% if note.vbr|length > 1 %}
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
