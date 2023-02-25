from typing import Tuple

from pydantic import BaseModel


class NotePositionParameters(BaseModel):
    point_1: Tuple[float, float]
    point_2: Tuple[float, float]
    inner_text: Tuple[float, float]
    upper_text: Tuple[float, float]
    lower_text: Tuple[float, float]
    text_size: float
