import math


class LambertW:
    @classmethod
    def evaluate(cls, x: float, branch: int = 0) -> float:
        if x < -1 / math.e:
            msg = "x must be greater than -1/e"
            raise ValueError(msg)
        if branch not in (0, -1):
            msg = "branch must be 0 or -1"
            raise ValueError(msg)
        if branch == -1 and x > 0:
            msg = "x must be less than 0 for branch -1"
            raise ValueError(msg)
        result = cls.estimate(x, branch)
        loop_remaining = 100
        while cls.test_result(result, x) and loop_remaining > 0:
            x0 = result
            y0 = result * math.exp(result)
            k = math.exp(x0) * (1 + x0)
            x1 = (x - y0) / k + x0
            result = x1
            loop_remaining -= 1
        if loop_remaining == 0:
            msg = "Cannot find solution"
            raise ValueError(msg)
        return result

    @classmethod
    def estimate(cls, x: float, branch: int = 0) -> float:
        if branch == -1:
            return -2 if x > -0.2706706 else -1 - math.acos(-4.11727 * x - 0.514659)
        else:
            return -1 + math.log(1 / math.e + math.e + x)

    @classmethod
    def test_result(cls, x: float, y: float) -> bool:
        fx = x * math.exp(x)
        if (delta := fx - y) == 0:
            return False
        delta_bits = math.log2(abs(y / delta))
        return delta_bits < 42
