class BaseWarning(UserWarning):
    """Base warning class for all warnings"""
    pass


class NotesWarning(BaseWarning):
    """Warning for notes"""
    pass


class LyricsWarning(BaseWarning):
    """Warning for lyrics"""
    pass


class ParamsWarning(BaseWarning):
    """Warning for params"""
    pass


class UnknownWarning(BaseWarning):
    """Warning for unknown"""
    pass
