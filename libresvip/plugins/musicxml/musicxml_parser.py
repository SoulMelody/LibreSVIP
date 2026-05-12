import dataclasses
import xml.etree.ElementTree as ET
from collections.abc import Iterator
from decimal import Decimal, InvalidOperation

from libresvip.core.constants import DEFAULT_PHONEME, TICKS_IN_BEAT
from libresvip.model.base import (
    Note,
    ParamCurve,
    Params,
    Points,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
)
from libresvip.model.point import Point
from libresvip.utils.music_math import note2midi

from .dynamics import dyn_label_to_volume, dynamics_label
from .fermata import FERMATA_STRETCH
from .models import mxml4
from .models.enums import StartStop, StartStopContinue, Syllabic
from .models.mxml4 import ScorePart, ScorePartwise
from .options import InputOptions


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _decimal(text: str | None) -> Decimal:
    if not text:
        return Decimal(0)
    try:
        return Decimal(text.strip())
    except InvalidOperation:
        return Decimal(0)


@dataclasses.dataclass
class _FermataInfo:
    note_index: int
    shape: str


@dataclasses.dataclass
class MusicXMLParser:
    options: InputOptions
    xml_bytes: bytes = b""
    _etree_root: ET.Element | None = dataclasses.field(default=None, init=False, repr=False)

    def _root(self) -> ET.Element | None:
        if self._etree_root is None and self.xml_bytes:
            self._etree_root = ET.fromstring(self.xml_bytes)
        return self._etree_root

    def _part_element(self, part_id: str | None) -> ET.Element | None:
        root = self._root()
        if root is None:
            return None
        for part in root.iter():
            if _local(part.tag) == "part" and (part_id is None or part.get("id") == part_id):
                return part
        return None

    def _walk_part_events(
        self, part_elem: ET.Element, divisions: int
    ) -> Iterator[tuple[str, int, ET.Element]]:
        """Yield (kind, absolute_tick, node) in document order.

        kind ∈ {"note", "direction", "sound"}. Time signatures advance
        measure boundaries via the typed walk; here we only need cursor
        movement so directions/sounds can be placed at the right tick.
        """
        rate = Decimal(TICKS_IN_BEAT) / Decimal(divisions)
        measure_start = 0
        current_ts = TimeSignature()

        for measure_elem in part_elem.findall("measure"):
            cursor = 0
            prev_note_start = 0

            time_node = measure_elem.find("attributes/time")
            if time_node is not None:
                beats = time_node.find("beats")
                beat_type = time_node.find("beat-type")
                if beats is not None and beat_type is not None and beats.text and beat_type.text:
                    current_ts = TimeSignature(
                        numerator=int(beats.text), denominator=int(beat_type.text)
                    )

            for child in measure_elem:
                tag = _local(child.tag)
                if tag == "note":
                    is_chord = child.find("chord") is not None
                    is_grace = child.find("grace") is not None
                    note_start = prev_note_start if is_chord else cursor
                    yield ("note", measure_start + note_start, child)
                    if not is_chord and not is_grace:
                        prev_note_start = note_start
                        cursor += int(_decimal(child.findtext("duration")) * rate)
                elif tag == "backup":
                    cursor -= int(_decimal(child.findtext("duration")) * rate)
                    prev_note_start = cursor
                elif tag == "forward":
                    cursor += int(_decimal(child.findtext("duration")) * rate)
                    prev_note_start = cursor
                elif tag == "direction":
                    offset_ticks = int(_decimal(child.findtext("offset")) * rate)
                    yield ("direction", measure_start + cursor + offset_ticks, child)
                elif tag == "sound":
                    yield ("sound", measure_start + cursor, child)

            measure_start += round(current_ts.bar_length())

    def parse_project(self, mxml: ScorePartwise) -> Project:
        part_nodes = mxml.part

        master_track = next((part for part in part_nodes if part.measure), None)
        assert master_track is not None
        (
            time_signatures,
            tempos,
            import_tick_rate,
            divisions,
        ) = self.parse_master_track(master_track)
        time_signatures = time_signatures or [TimeSignature()]
        tempos = tempos or [SongTempo()]

        tracks: list[SingingTrack] = []
        track_fermatas: list[list[_FermataInfo]] = []
        for index, part in enumerate(part_nodes):
            score_part = None
            if mxml.part_list is not None and part.id is not None:
                score_part = next(
                    (item for item in mxml.part_list.score_part if item.id == part.id),
                    None,
                )
            track, fermatas = self.parse_track(index, part, score_part, import_tick_rate)
            if self.options.import_dynamics:
                part_elem = self._part_element(part.id)
                if part_elem is not None:
                    self._populate_volume(track, part_elem, divisions)
            tracks.append(track)
            track_fermatas.append(fermatas)

        if self.options.apply_fermata_stretch:
            for index, (track, fermatas) in enumerate(zip(tracks, track_fermatas)):
                if not fermatas:
                    continue
                self._apply_fermata_stretch(
                    track,
                    fermatas,
                    tempos if index == 0 else None,
                )

        return Project(
            track_list=tracks,
            time_signature_list=time_signatures,
            song_tempo_list=tempos,
        )

    def parse_master_track(
        self, part_node: ScorePartwise.Part
    ) -> tuple[list[TimeSignature], list[SongTempo], float, int]:
        measure_nodes = part_node.measure
        assert measure_nodes[0].attributes[0].divisions is not None
        divisions = int(measure_nodes[0].attributes[0].divisions)
        import_tick_rate = TICKS_IN_BEAT / divisions
        tempos: list[SongTempo] = []
        time_signatures: list[TimeSignature] = []
        current_time_signature = TimeSignature()
        for i, measure_node in enumerate(measure_nodes):
            if (
                len(measure_node.attributes)
                and len(measure_node.attributes[0].time)
                and (time_signature_node := measure_node.attributes[0].time[0])
            ):
                bar_index = int(time_signature_node.number or i)
                numerator = int(time_signature_node.beats[0])
                denominator = int(time_signature_node.beat_type[0])
                current_time_signature = TimeSignature(
                    bar_index=bar_index, numerator=numerator, denominator=denominator
                )
                time_signatures.append(current_time_signature)

        if self.options.import_tempo:
            part_elem = self._part_element(part_node.id)
            if part_elem is not None:
                for kind, tick, node in self._walk_part_events(part_elem, divisions):
                    if kind == "direction":
                        sound = node.find("sound")
                        if sound is not None and sound.get("tempo"):
                            tempos.append(
                                SongTempo(position=tick, bpm=float(sound.get("tempo", "0")))
                            )
                    elif kind == "sound" and node.get("tempo"):
                        tempos.append(SongTempo(position=tick, bpm=float(node.get("tempo", "0"))))
            else:
                # No xml_bytes plumbed (e.g. legacy callers): fall back to typed walk.
                tick_position = 0
                for measure_node in measure_nodes:
                    sound_nodes = measure_node.sound
                    if len(sound_nodes) and (sound_node := sound_nodes[0]).tempo:
                        tempos.append(
                            SongTempo(position=tick_position, bpm=float(sound_node.tempo))
                        )
                    tick_position += round(current_time_signature.bar_length())

        tempos.sort(key=lambda t: t.position)
        deduped: list[SongTempo] = []
        for t in tempos:
            if deduped and deduped[-1].position == t.position:
                deduped[-1] = t
            else:
                deduped.append(t)
        return time_signatures, deduped, import_tick_rate, divisions

    def _populate_volume(self, track: SingingTrack, part_elem: ET.Element, divisions: int) -> None:
        points: list[Point] = []
        open_wedges: dict[int, tuple[int, str, int]] = {}
        last_volume = 0

        for kind, tick, node in self._walk_part_events(part_elem, divisions):
            if kind != "direction":
                continue
            for dt in node.findall("direction-type"):
                for d in dt.findall("dynamics"):
                    for child in d:
                        label = _local(child.tag)
                        if dynamics_label(label):
                            last_volume = dyn_label_to_volume(label)
                            points.append(Point(tick, last_volume))
                            break
                for w in dt.findall("wedge"):
                    try:
                        n = int(w.get("number") or 1)
                    except ValueError:
                        n = 1
                    wtype = w.get("type")
                    if wtype in ("crescendo", "diminuendo"):
                        open_wedges[n] = (tick, wtype, last_volume)
                        points.append(Point(tick, last_volume))
                    elif wtype == "stop" and n in open_wedges:
                        open_wedges.pop(n)
                        if w.get("niente") == "yes":
                            points.append(Point(tick, dyn_label_to_volume("ppppp")))
                            last_volume = dyn_label_to_volume("ppppp")
                        else:
                            points.append(Point(tick, last_volume))
            sound = node.find("sound")
            if sound is not None and sound.get("dynamics"):
                v = round(_decimal(sound.get("dynamics")) * Decimal(127) / Decimal(100))
                last_volume = dyn_label_to_volume_from_velocity(v)
                points.append(Point(tick, last_volume))

        if not points:
            return
        points.sort(key=lambda p: p.x)
        deduped: list[Point] = []
        for p in points:
            if deduped and deduped[-1].x == p.x:
                deduped[-1] = p
            else:
                deduped.append(p)
        track.edited_params = Params(volume=ParamCurve(points=Points(root=deduped)))

    def _apply_fermata_stretch(
        self,
        track: SingingTrack,
        fermatas: list[_FermataInfo],
        tempos: list[SongTempo] | None,
    ) -> None:
        index_to_shape = {f.note_index: f.shape for f in fermatas}
        thresholds: list[tuple[int, int]] = []
        shift = 0
        for i, note in enumerate(track.note_list):
            note.start_pos += shift
            if i in index_to_shape:
                shape = index_to_shape[i] or "normal"
                factor = FERMATA_STRETCH.get(shape, 1.5)
                extra = round(note.length * (factor - 1))
                if extra > 0:
                    threshold = note.start_pos + note.length
                    note.length += extra
                    thresholds.append((threshold, extra))
                    shift += extra

        if not thresholds:
            return

        def _delta(x: int) -> int:
            return sum(extra for thr, extra in thresholds if x > thr)

        if track.edited_params and track.edited_params.volume:
            existing = track.edited_params.volume.points.root
            new_points = [Point(p.x + _delta(p.x), p.y) for p in existing]
            track.edited_params.volume = ParamCurve(points=Points(root=new_points))
        if tempos is not None:
            for tempo in tempos:
                tempo.position += _delta(tempo.position)

    def syllabic_status(self, lyric: mxml4.Lyric) -> Syllabic:
        if lyric.syllabic:
            return lyric.syllabic[0]
        return Syllabic.SINGLE

    def parse_track(
        self,
        track_index: int,
        part_node: ScorePartwise.Part,
        score_part: ScorePart | None,
        import_tick_rate: float,
    ) -> tuple[SingingTrack, list[_FermataInfo]]:
        track_name = (
            score_part.part_name.value
            if score_part is not None and score_part.part_name is not None
            else f"Track {track_index + 1}"
        )
        notes: list[Note] = []
        fermatas: list[_FermataInfo] = []
        is_inside_note = False
        measure_nodes = part_node.measure
        tick_position = 0
        previous_tick_position = 0
        incomplete_lyric_note: Note | None = None
        duration: int | None = None
        for measure_node in measure_nodes:
            for note_node in measure_node.content:
                if isinstance(note_node, mxml4.Backup):
                    duration = int(float(note_node.duration) * import_tick_rate)
                    tick_position -= duration
                    previous_tick_position = tick_position
                    continue

                if isinstance(note_node, mxml4.Forward):
                    duration = int(float(note_node.duration) * import_tick_rate)
                    tick_position += duration
                    previous_tick_position = tick_position
                    continue

                duration_nodes = note_node.duration
                duration = (
                    int(float(duration_nodes[0]) * import_tick_rate)
                    if len(duration_nodes)
                    else None
                )
                if not duration:
                    if note_node.grace:
                        continue
                    else:
                        msg = "Duration not found"
                        raise ValueError(msg)

                rest_nodes = note_node.rest
                if rest_nodes:
                    tick_position += duration
                    continue

                pitch_node = note_node.pitch[0]
                step = pitch_node.step
                assert step is not None
                assert pitch_node.octave is not None
                alter_node = pitch_node.alter
                alter = int(alter_node) if alter_node else 0
                octave = int(pitch_node.octave)
                key = note2midi(f"{step.value}{octave}") + alter

                lyric_nodes = note_node.lyric
                if any(
                    slur.type_value in [StartStopContinue.CONTINUE, StartStopContinue.STOP]
                    for notation in note_node.notations
                    for slur in notation.slur
                ):
                    lyric = "-"
                elif len(lyric_nodes) and len(lyric_nodes[0].text):
                    lyric = lyric_nodes[0].text[0].value
                else:
                    lyric = DEFAULT_PHONEME

                # In MusicXml, <chord/> means the note forms a chord with the previous note.
                # It starts at the same tick position as the previous note.
                chord_node = note_node.chord
                if chord_node:
                    tick_position = previous_tick_position

                if not is_inside_note:
                    note = Note(
                        key_number=key,
                        lyric=lyric,
                        start_pos=tick_position,
                        length=duration,
                    )
                    if len(lyric_nodes):
                        syllabic = self.syllabic_status(lyric_nodes[0])
                        if syllabic == Syllabic.BEGIN:
                            incomplete_lyric_note = note
                        elif syllabic == Syllabic.END and incomplete_lyric_note is not None:
                            incomplete_lyric_note.lyric += lyric
                            incomplete_lyric_note = None
                            note.lyric = "+"
                        elif syllabic == Syllabic.MIDDLE and incomplete_lyric_note is not None:
                            incomplete_lyric_note.lyric += lyric
                            note.lyric = "+"
                    notes.append(note)
                    note_index = len(notes) - 1
                    fermata_shape = next(
                        (
                            (f.value.value if f.value else "")
                            for notation in note_node.notations
                            for f in notation.fermata
                        ),
                        None,
                    )
                    if fermata_shape is not None:
                        fermatas.append(_FermataInfo(note_index=note_index, shape=fermata_shape))
                else:
                    notes[-1] = notes[-1].model_copy(
                        update={
                            "length": notes[-1].length + duration,
                        }
                    )

                previous_tick_position = tick_position
                tick_position += duration

                tie_nodes = note_node.tie
                if len(tie_nodes) > 0 and (tie_node := tie_nodes[0]) and tie_node.type_value:
                    if tie_node.type_value == StartStop.START:
                        is_inside_note = True
                    elif tie_node.type_value == StartStop.STOP:
                        is_inside_note = False

        notes.sort(key=lambda n: (n.start_pos, n.key_number))
        return (
            SingingTrack(
                title=track_name,
                note_list=notes,
            ),
            fermatas,
        )


def dyn_label_to_volume_from_velocity(velocity: int) -> int:
    from libresvip.plugins.mid.midi_parser import cc11_to_db_change

    return round(cc11_to_db_change(velocity))
