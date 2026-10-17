from libresvip.plugins.ustx.model import USTXProject


def test_parse_expressions_without_flag() -> None:
    # OpenUtau's YAML serializer omits null values (DefaultValuesHandling.OmitNull) and
    # UExpressionDescriptor.flag is a nullable string, so a ustx file may leave the
    # `flag` key out entirely or set it to null. Loading such a file used to raise a
    # pydantic ValidationError.
    project = USTXProject.model_validate(
        {
            "name": "test",
            "ustx_version": "0.7",
            "expressions": {
                "dyn": {
                    "name": "dynamics",
                    "abbr": "dyn",
                    "type": "Curve",
                    "min": -240,
                    "max": 120,
                    "default_value": 0,
                    "is_flag": False,
                },
                "vel": {
                    "name": "velocity",
                    "abbr": "vel",
                    "type": "Numerical",
                    "min": 0,
                    "max": 200,
                    "default_value": 100,
                    "is_flag": False,
                },
                "pitd": {
                    "name": "pitch deviation",
                    "abbr": "pitd",
                    "type": "Curve",
                    "min": -1200,
                    "max": 1200,
                    "default_value": 0,
                    "is_flag": False,
                    "flag": None,
                },
            },
        }
    )
    assert project.expressions is not None
    assert project.expressions["dyn"].flag is None
    assert project.expressions["vel"].flag is None
    assert project.expressions["pitd"].flag is None


def test_parse_masked_curve_expression() -> None:
    # OpenUtau added a fourth expression type, `MaskedCurve` (upstream commit
    # d01afa28), used by `rpit` (rendered pitch) and `pito` (pitch override).
    # The discriminated union only knew Curve/Numerical/Options, so every
    # project saved with those expressions failed to load.
    project = USTXProject.model_validate(
        {
            "name": "test",
            "ustx_version": "0.10",
            "expressions": {
                "rpit": {
                    "name": "rendered pitch (masked curve)",
                    "abbr": "rpit",
                    "type": "MaskedCurve",
                    "min": 2400,
                    "max": 10800,
                    "default_value": 6000,
                    "is_flag": False,
                    "flag": "",
                },
                "pito": {
                    "name": "pitch override (masked curve)",
                    "abbr": "pito",
                    "type": "MaskedCurve",
                    "min": 2400,
                    "max": 10800,
                    "default_value": 6000,
                    "is_flag": False,
                },
            },
        }
    )
    assert project.expressions is not None
    assert project.expressions["rpit"].type_ == "MaskedCurve"
    assert project.expressions["pito"].type_ == "MaskedCurve"
    assert project.expressions["pito"].flag is None
