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
NoteNum={{ note.note_num }}{% if note.optional_attrs|length > 1 %}{% for attr in note.optional_attrs %}{% if attr.key == 'PreUtterance' %}
PreUtterance={{ attr.pre_utterance }}{% elif attr.key == 'VoiceOverlap' %}
VoiceOverlap={{ attr.voice_overlap }}{% elif attr.key == 'Intensity' %}
Intensity={{ attr.intensity }}{% elif attr.key in ['Modulation', 'Moduration'] %}
Modulation={{ attr.modulation }}{% elif attr.key == 'StartPoint' %}
StartPoint={{ attr.start_point }}{% elif attr.key == 'Envelope' %}
Envelope={{ attr.envelope.base.p1 }},{{ attr.envelope.base.p2 }},{{ attr.envelope.base.p3 }},{{ attr.envelope.base.v1 }},{{ attr.envelope.base.v2 }},{{ attr.envelope.base.v3 }},{{ attr.envelope.base.v4 }}\
{% if attr.envelope.v5 %}\
,%,{{ attr.envelope.p4 }},{{ attr.envelope.p5 }},{{ attr.envelope.v5 }}{% elif attr.envelope.p5 %}\
,%,{{ attr.envelope.p4 }},{{ attr.envelope.p5 }}{% elif attr.envelope.p4 %}\
,,{{ attr.envelope.p4 }}{% endif %}{% elif attr.key == 'Tempo' %}
Tempo={{ attr.tempo }}{% elif attr.key == 'Velocity' %}
Velocity={{ attr.velocity }}{% elif attr.key == 'Label' %}
Label={{ attr.label }}{% elif attr.key == 'Flags' %}
Flags={{ attr.flags }}{% elif attr.key == 'PBType' %}
PBType={{ attr.pitchbend_type }}{% elif attr.key == 'PBStart' %}
PBStart={{ attr.pitchbend_start }}{% elif attr.key in ['Piches', 'Pitches', 'PitchBend'] %}
PitchBend={{ attr.pitch_bend_points|join(',') }}{% elif attr.key == 'PBS' %}
PBS={{ attr.pbs_1 }}{%if attr.pbs_2 %};{{ attr.pbs_2 }}{% endif %}{% elif attr.key == 'PBW' %}
PBW={{ attr.pbw | join(',') }}{% elif attr.key == 'PBY' %}
PBY={{ attr.pby | join(',') }}{% elif attr.key == 'PBM' %}
PBM={% for pbm in attr.pbm %}{{ pbm.text }}{% if not loop.last %},{% endif %}{% endfor %}{% elif attr.key == 'VBR' %}
VBR={{ attr.vbr | join(',') }}{% elif attr.key.startswith('$') %}
{{ attr.key }}={{ attr.value }}{% endif %}{% endfor %}{% endif %}{% endfor %}
[#TRACKEND]{% endif %}
"""
)


def render_ust(
    ust_project: UTAUProject, output_path: pathlib.Path, encoding: str = "utf-8"
):
    output_path.write_text(
        UST_TEMPLATE.render(ust_project=ust_project), encoding=encoding
    )
