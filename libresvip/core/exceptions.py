class InvalidFileTypeError(Exception):
    pass


class UnsupportedProjectVersionError(InvalidFileTypeError):
    pass


class NoTrackError(Exception):
    pass


class NotesOverlappedError(Exception):
    pass


class ParamsError(Exception):
    pass
