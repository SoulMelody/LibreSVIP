import sys

from libresvip.model.base import ParamCurve, Point, Points


def test_curve_split_01():
    points = Points(
        __root__=[Point(1, 1), Point(2, 1), Point(3, 0), Point(4, 1), Point(5, 1)]
    )
    curve = ParamCurve.construct(points=points)
    segments = curve.split_into_segments()
    assert len(segments) == 1
    assert segments[0] == [(1, 1), (2, 1), (3, 0), (4, 1), (5, 1)]


def test_curve_split_02():
    points = Points(
        __root__=[
            Point(1, 0),
            Point(2, 0),
            Point(3, 1),
            Point(4, 1),
            Point(5, 0),
            Point(6, 0),
            Point(7, 1),
            Point(8, 1),
            Point(9, 0),
            Point(10, 0),
        ]
    )
    curve = ParamCurve.construct(points=points)
    segments = curve.split_into_segments()
    assert len(segments) == 2
    assert segments[0] == [
        (3, 1),
        (4, 1),
    ]
    assert segments[1] == [
        (7, 1),
        (8, 1),
    ]


def test_curve_split_04():
    points = Points(
        __root__=[
            Point(-192000, 0),
            Point(2, 1),
            Point(3, 1),
            Point(sys.maxsize // 2, 0),
        ]
    )
    curve = ParamCurve.construct(points=points)
    segments = curve.split_into_segments()
    assert len(segments) == 1
    assert segments[0] == [
        (2, 1),
        (3, 1),
    ]
