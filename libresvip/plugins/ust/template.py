import pathlib

from jinja2 import Template

from .model import UTAUProject

UST_TEMPLATE = Template(
    """\
[#VERSION]
UST Version={{ ust_project.ust_version }}{% if ust_project.charset %}
Charset={{ ust_project.charset }}{% endif %}
[#SETTING]{% if ust_project.tempo | round(2) %}
Tempo={{ ust_project.tempo }}{% endif %}{% if ust_project.track_count %}
Tracks={{ ust_project.track_count }}{% endif %}{% if ust_project.project_name %}
Project={{ ust_project.project_name }}{% endif %}{% if ust_project.voice_dir %}
VoiceDir={{ ust_project.voice_dir }}{% endif %}{% if ust_project.out_file %}
OutFile={{ ust_project.out_file }}{% endif %}{% if ust_project.cache_dir %}
CacheDir={{ ust_project.cache_dir }}{% endif %}{% if ust_project.tool1 %}
Tool1={{ ust_project.tool1 }}{% endif %}{% if ust_project.tool2 %}
Tool2={{ ust_project.tool2 }}{% endif %}{% if ust_project.pitch_mode2 %}
Mode2={{ ust_project.pitch_mode2 | round }}{% endif %}{% if ust_project.autoren %}
Autoren={{ ust_project.autoren }}{% endif %}{% if ust_project.flags %}
Flags={{ ust_project.flags }}{% endif %}{% if ust_project.track | length > 0 %}{% for note in ust_project.track[0].notes %}
[#{{ note.note_type }}]
Length={{ note.length }}
Lyric={{ note.lyric }}
NoteNum={{ note.note_num }}{% if note.pre_utterance %}
PreUtterance={{ note.pre_utterance }}{% endif %}{% if note.voice_overlap %}
VoiceOverlap={{ note.voice_overlap | round(2) }}{% endif %}{% if note.intensity %}
Intensity={{ note.intensity }}{% endif %}{% if note.modulation %}
Modulation={{ note.modulation }}{% endif %}{% if note.start_point %}
StartPoint={{ note.start_point | round(2) }}{% endif %}{% if note.envelope %}
Envelope={{ note.envelope.p1 }},{{ note.envelope.p2 }},{{ note.envelope.p3 }},{{ note.envelope.v1 }},{{ note.envelope.v2 }},{{ note.envelope.v3 }},{{ note.envelope.v4 }}\
{% if note.envelope.v5 %}\
,%,{{ note.envelope.p4 }},{{ note.envelope.p5 }},{{ note.envelope.v5 }}{% elif note.envelope.p5 %}\
,%,{{ note.envelope.p4 }},{{ note.envelope.p5 }}{% elif note.envelope.p4 %}\
,,{{ note.envelope.p4 }}{% endif %}{% endif %}{% if note.tempo %}
Tempo={{ note.tempo | round(2) }}{% endif %}{% if note.velocity %}
Velocity={{ note.velocity | round(2) }}{% endif %}{% if note.label %}
Label={{ note.label }}{% endif %}{% if note.flags %}
Flags={{ note.flags }}{% endif %}{% if note.pitchbend_type %}
PBType={{ note.pitchbend_type }}{% endif %}{% if note.pitchbend_start %}
PBStart={{ note.pitchbend_start }}{% endif %}{% if note.pitch_bend_points|length > 0 %}
PitchBend={{ note.pitch_bend_points|join(',') }}{% endif %}{% if note.pbs|length > 0 %}
PBS={{ note.pbs | join(';') }}{% endif %}{% if note.pbw|length > 0 %}
PBW={{ note.pbw | join(',') }}{% endif %}{% if note.pby|length > 0 %}
PBY={{ note.pby | join(',') }}{% endif %}{% if note.pbm|length > 0 %}
PBM={{ note.pbm | join(',') }}{% endif %}{% if note.vbr %}
VBR={{ note.vbr.length }},{{ note.vbr.period }},{% if note.vbr.depth is defined %}\
{{ note.vbr.depth }}{% endif %},{% if note.vbr.fade_in is defined %}\
{{ note.vbr.fade_in }}{% endif %},{% if note.vbr.fade_out is defined %}\
{{ note.vbr.fade_out }}{% endif %},{% if note.vbr.phase_shift is defined %}\
{{ note.vbr.phase_shift }}{% endif %},{% if note.vbr.shift is defined %}\
{{ note.vbr.shift }}{% endif %}{% endif %}{% endfor %}
[#TRACKEND]{% endif %}
"""
)


def render_ust(
    ust_project: UTAUProject,
    output_path: pathlib.Path,
    encoding: str = "utf-8",
) -> None:
    output_path.write_bytes(UST_TEMPLATE.render(ust_project=ust_project).encode(encoding))
