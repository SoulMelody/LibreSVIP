import math


class LambertW:
    @classmethod
    def evaluate(cls, x: float, branch: int = 0) -> float:
        if x < -1 / math.e:
            raise ValueError("x must be greater than -1/e")
        if branch not in (0, -1):
            raise ValueError("branch must be 0 or -1")
        if branch == -1 and x > 0:
            raise ValueError("x must be less than 0 for branch -1")
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
            raise ValueError("Cannot find solution")
        return result

    @classmethod
    def estimate(cls, x: float, branch: int = 0) -> float:
        if branch == -1:
            if x > -0.2706706:
                return -2
            else:
                return -1 - math.acos(-4.11727 * x - 0.514659)
        else:
            return -1 + math.log(1 / math.e + math.e + x)

    @classmethod
    def test_result(cls, x: float, y: float) -> bool:
        fx = x * math.exp(x)
        delta = fx - y
        delta_bits = math.log(abs(y / delta), 2)
        return delta_bits < 42
