class BaseWarning(UserWarning):
    """Base warning class for all warnings"""


class NotesWarning(BaseWarning):
    """Warning for notes"""


class LyricsWarning(BaseWarning):
    """Warning for lyrics"""


class ParamsWarning(BaseWarning):
    """Warning for params"""


class UnknownWarning(BaseWarning):
    """Warning for unknown"""
