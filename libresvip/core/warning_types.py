class BaseWarning(UserWarning):
    """Base warning class for all warnings"""


class TimeSignatureWarning(BaseWarning):
    """Warning for time signatures"""


class TempoWarning(BaseWarning):
    """Warning for tempos"""


class NotesWarning(BaseWarning):
    """Warning for notes"""


class PhonemeWarning(BaseWarning):
    """Warning for phoneme"""


class ParamsWarning(BaseWarning):
    """Warning for params"""


class UnknownWarning(BaseWarning):
    """Warning for unknown"""
