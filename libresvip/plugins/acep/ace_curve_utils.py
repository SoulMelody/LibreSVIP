import statistics
from typing import Callable, Optional

from pydantic import Field, RootModel

from libresvip.core.time_interval import RangeInterval
from libresvip.model.base import BaseModel


class AcepParamCurve(BaseModel):
    curve_type: str = Field("data", alias="type")
    offset: int = 0
    values: list[float] = Field(default_factory=list)
    points: Optional[list[float]] = None
    points_vuv: Optional[list[float]] = Field(None, alias="pointsVUV")

    def transform(self, value_transform: Callable[[float], float]):
        return self.model_copy(
            update={"values": [value_transform(each) for each in self.values]},
            deep=True,
        )


class AcepParamCurveList(RootModel[list[AcepParamCurve]]):
    root: list[AcepParamCurve] = Field(default_factory=list)

    def plus(self, others, default_value: float, transform: Callable[[float], float]):
        if not others:
            return self
        result_ranges = RangeInterval(
            [
                (curve.offset, curve.offset + len(curve.values))
                for curve in (self.root + others.root)
            ],
        ).sub_ranges()
        result_curve_list = type(self)()
        for start, end in result_ranges:
            result_curve = AcepParamCurve()
            result_curve.offset = start
            result_curve.values = [0.0] * (end - start)
            for self_curve in (
                curve for curve in self.root if start <= curve.offset < end
            ):
                index = self_curve.offset - start
                for value in self_curve.values:
                    result_curve.values[index] = value
                    index += 1
            for other_curve in (
                curve for curve in others.root if start <= curve.offset < end
            ):
                index = other_curve.offset - start
                for value in other_curve.values:
                    if result_curve.values[index] == 0.0:
                        result_curve.values[index] = default_value
                    result_curve.values[index] += transform(value)
                    index += 1
            result_curve_list.root.append(result_curve)
        return result_curve_list

    def exclude(self, predicate: Callable[[float], bool]):
        result = type(self)()
        for curve in self.root:
            buffer = []
            pos = curve.offset
            for value in curve.values:
                pos += 1
                if predicate(value):
                    if buffer:
                        result.root.append(
                            AcepParamCurve(offset=pos - len(buffer), values=buffer)
                        )
                        buffer = []
                else:
                    buffer.append(value)

            if buffer:
                result.root.append(
                    AcepParamCurve(offset=pos - len(buffer), values=buffer)
                )

        return result

    def z_score_normalize(self, d=1, b=0):
        if not self.root:
            return self
        points = sum(curve.values for curve in self.root)
        miu = statistics.mean(points)
        sigma = statistics.stdev(points)
        return type(self)(
            root=[
                curve.transform(lambda x: (x - miu) / sigma * d + b)
                for curve in self.root
            ]
        )

    def minmax_normalize(self, r=1, b=0):
        if not self.root:
            return self
        minmax = sum((curve.values for curve in self.root), [])
        min_ = min(minmax)
        max_ = max(minmax)
        return type(self)(
            root=[
                curve.transform(lambda x: r * (2 * (x - min_) / (max_ - min_) - 1) + b)
                for curve in self.root
            ]
            if abs(max_ - min_) > 1e-3
            else [curve.transform(lambda x: 0) for curve in self.root]
        )
