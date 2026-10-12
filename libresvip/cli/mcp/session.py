from collections import OrderedDict
from typing import TypedDict
from uuid import uuid4

from libresvip.model.base import Project, SingingTrack


class ProjectSummary(TypedDict):
    handle: str
    track_count: int
    singing_track_count: int
    note_count: int
    tempo_count: int
    time_signature_count: int
    first_bpm: float | None
    tracks: list[str]
    warnings: list[str]


class ProjectSession:
    def __init__(self, capacity: int = 8) -> None:
        self._projects: OrderedDict[str, Project] = OrderedDict()
        self.capacity = capacity

    def put(self, project: Project) -> str:
        handle = uuid4().hex
        self._projects[handle] = project
        self._projects.move_to_end(handle)
        while len(self._projects) > self.capacity:
            self._projects.popitem(last=False)
        return handle

    def get(self, handle: str) -> Project | None:
        project = self._projects.get(handle)
        if project is not None:
            self._projects.move_to_end(handle)
        return project

    def replace(self, handle: str, project: Project) -> None:
        self._projects[handle] = project
        self._projects.move_to_end(handle)

    def drop(self, handle: str) -> bool:
        return self._projects.pop(handle, None) is not None


def summarize(handle: str, project: Project, warnings: list[str] | None = None) -> ProjectSummary:
    tracks = []
    note_count = 0
    singing_track_count = 0
    for track in project.track_list:
        if isinstance(track, SingingTrack):
            singing_track_count += 1
            note_count += len(track.note_list)
            tracks.append(f"{track.title or '(untitled)'} ({len(track.note_list)} notes)")
        else:
            tracks.append(f"{track.title or '(untitled)'} (instrumental)")
    return {
        "handle": handle,
        "track_count": len(project.track_list),
        "singing_track_count": singing_track_count,
        "note_count": note_count,
        "tempo_count": len(project.song_tempo_list),
        "time_signature_count": len(project.time_signature_list),
        "first_bpm": project.song_tempo_list[0].bpm if project.song_tempo_list else None,
        "tracks": tracks,
        "warnings": warnings or [],
    }
