from pydantic import BaseModel


class NotePositionParameters(BaseModel):
    point_1: tuple[float, float]
    point_2: tuple[float, float]
    inner_text: tuple[float, float]
    upper_text: tuple[float, float]
    lower_text: tuple[float, float]
    text_size: float
