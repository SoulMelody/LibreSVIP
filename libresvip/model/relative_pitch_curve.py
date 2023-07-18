from bisect import bisect_right

from libresvip.model.base import BaseModel, Field, Note, ParamCurve, Points
from libresvip.model.point import Point


class RelativePitchCurve(BaseModel):
    points: Points = Field(default_factory=Points)

    def to_absolute(self, note_list: list[Note]) -> ParamCurve:
        param_curve = ParamCurve()
        boundries = [
            (note.start_pos, note.end_pos)
            for note in note_list
        ]
        prev_index = -1
        for point in self.points:
            note_index = bisect_right(boundries, (point.x, point.x)) - 1
            if note_index < 0:
                continue
            elif note_index > prev_index:
                prev_index = note_index
                if len(param_curve.points) > 0:
                    param_curve.points.append(
                        Point(
                            x=param_curve.points[-1].x,
                            y=-100
                        )
                    )
                else:
                    param_curve.points.append(
                        Point.start_point()
                    )
                param_curve.points.append(
                    Point(
                        x=point.x + 1920,
                        y=-100
                    )
                )
            note = note_list[note_index]
            if not note.start_pos <= point.x < note.end_pos:
                continue
            y = note.key_number * 100 + point.y
            param_curve.points.append(Point(x=point.x + 1920, y=y))
        if len(param_curve.points) > 0:
            param_curve.points.append(
                Point.end_point()
            )
        return param_curve
