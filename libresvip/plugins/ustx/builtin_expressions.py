from typing import Literal, Optional

from pydantic import Field

from libresvip.plugins.ustx.model import (
    CurveExpression,
    NumericalExpression,
    OptionsExpression,
)


class Alt(NumericalExpression):
    name: Literal["alternate"]
    abbr: Literal["alt"]
    min_: int = Field(0, alias="min")
    max_: int = Field(16, alias="max")
    default_value: Optional[int] = 0
    is_flag: Optional[bool] = False
    flag: Optional[str] = ""


class Atk(NumericalExpression):
    name: Literal["attack"]
    abbr: Literal["atk"]
    min_: int = Field(0, alias="min")
    max_: int = Field(200, alias="max")
    default_value: Optional[int] = 100
    is_flag: Optional[bool] = False
    flag: Optional[str] = ""


class Bre(NumericalExpression):
    name: Literal["breath"]
    abbr: Literal["bre"]
    min_: Optional[int] = 0
    max_: Optional[int] = 100
    default_value: Optional[int] = 0
    is_flag: Optional[bool] = True
    flag: Optional[str] = "B"


class Brec(CurveExpression):
    name: Literal["breathiness (curve)"]
    abbr: Literal["brec"]
    min_: Optional[int] = -100
    max_: Optional[int] = 100
    default_value: Optional[int] = 0
    is_flag: Optional[bool] = False
    flag: Optional[str] = ""


class Clr(OptionsExpression):
    name: Literal["voice color"]
    abbr: Literal["clr"]
    min_: Optional[int] = 0
    max_: Optional[int] = -1
    default_value: Optional[int] = 0
    is_flag: Optional[bool] = False


class Dec(NumericalExpression):
    name: Literal["decay"]
    abbr: Literal["dec"]
    min_: Optional[int] = 0
    max_: Optional[int] = 100
    default_value: Optional[int] = 0
    is_flag: Optional[bool] = False
    flag: Optional[str] = ""


class Dyn(CurveExpression):
    name: Literal["dynamics (curve)"]
    abbr: Literal["dyn"]
    min_: Optional[int] = -240
    max_: Optional[int] = 120
    default_value: Optional[int] = 0
    is_flag: Optional[bool] = False
    flag: Optional[str] = ""


class Eng(OptionsExpression):
    name: Literal["resampler engine"]
    abbr: Literal["eng"]
    min_: Optional[int] = 0
    max_: Optional[int] = 1
    default_value: Optional[int] = 0
    is_flag: Optional[bool] = False


class Gen(NumericalExpression):
    name: Literal["gender"]
    abbr: Literal["gen"]
    min_: Optional[int] = -100
    max_: Optional[int] = 100
    default_value: Optional[int] = 0
    is_flag: Optional[bool] = True
    flag: Optional[str] = "g"


class Genc(CurveExpression):
    name: Literal["gender (curve)"]
    abbr: Literal["genc"]
    min_: Optional[int] = -100
    max_: Optional[int] = 100
    default_value: Optional[int] = 0
    is_flag: Optional[bool] = False
    flag: Optional[str] = ""


class Lpf(NumericalExpression):
    name: Literal["lowpass"]
    abbr: Literal["lpf"]
    min_: Optional[int] = 0
    max_: Optional[int] = 100
    default_value: Optional[int] = 0
    is_flag: Optional[bool] = True
    flag: Optional[str] = "H"


class Mod(NumericalExpression):
    name: Literal["modulation"]
    abbr: Literal["mod"]
    min_: Optional[int] = 0
    max_: Optional[int] = 100
    default_value: Optional[int] = 0
    is_flag: Optional[bool] = False
    flag: Optional[str] = ""


class Pitd(CurveExpression):
    name: Literal["pitch deviation (curve)"]
    abbr: Literal["pitd"]
    min_: Optional[int] = -1200
    max_: Optional[int] = 1200
    default_value: Optional[int] = 0
    is_flag: Optional[bool] = False
    flag: Optional[str] = ""


class Shfc(CurveExpression):
    name: Literal["tone shift (curve)"]
    abbr: Literal["shfc"]
    min_: Optional[int] = -1200
    max_: Optional[int] = 1200
    default_value: Optional[int] = 0
    is_flag: Optional[bool] = False
    flag: Optional[str] = ""


class Shft(NumericalExpression):
    name: Literal["tone shift"]
    abbr: Literal["shft"]
    min_: Optional[int] = -36
    max_: Optional[int] = 36
    default_value: Optional[int] = 0
    is_flag: Optional[bool] = False
    flag: Optional[str] = ""


class Tenc(CurveExpression):
    name: Literal["tension (curve)"]
    abbr: Literal["tenc"]
    min_: Optional[int] = -100
    max_: Optional[int] = 100
    default_value: Optional[int] = 0
    is_flag: Optional[bool] = False
    flag: Optional[str] = ""


class Vel(NumericalExpression):
    name: Literal["velocity"]
    abbr: Literal["vel"]
    min_: Optional[int] = 0
    max_: Optional[int] = 200
    default_value: Optional[int] = 100
    is_flag: Optional[bool] = False
    flag: Optional[str] = ""


class Voic(CurveExpression):
    name: Literal["voicing (curve)"]
    abbr: Literal["voic"]
    min_: Optional[int] = 0
    max_: Optional[int] = 100
    default_value: Optional[int] = 100
    is_flag: Optional[bool] = False
    flag: Optional[str] = ""


class Vol(NumericalExpression):
    name: Literal["volume"]
    abbr: Literal["vol"]
    min_: Optional[int] = 0
    max_: Optional[int] = 200
    default_value: Optional[int] = 100
    is_flag: Optional[bool] = False
    flag: Optional[str] = ""
