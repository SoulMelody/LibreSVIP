def interpolate_hermite(
    x: list[float],
    y: list[float],
    x_new: list[float],
    k0: float = 0,
    kn: float = 0,
) -> list[float]:
    list1: list[float] = []
    if not x:
        return [0] * len(x_new)
    list2: list[float] = [k0]
    list2.extend((y[j + 1] - y[j - 1]) / (x[j + 1] - x[j - 1]) for j in range(1, len(x) - 1))
    list2.append(kn)
    num: int = 0
    for item in x_new:
        while num < len(x) and x[num] < item:
            num += 1
        point1: tuple[float, float]
        num2: float
        if num == 0:
            point1 = item, y[0]
            num2 = 0
        else:
            point1 = (x[num - 1], y[num - 1])
            num2 = list2[num - 1]
        point2: tuple[float, float]
        num3: float
        if num == len(x):
            point2 = item, y[len(x) - 1]
            num3 = 0
        else:
            point2 = (x[num], y[num])
            num3 = list2[num]
        if point1[0] == point2[0]:
            list1.append((point1[1] + point2[1]) / 2)
        else:
            num4: float = item - point1[0]
            num5: float = item - point2[0]
            t: float = num4 / (point2[0] - point1[0])
            t2: float = num5 / (point1[0] - point2[0])
            list1.append(
                ((1 + 2 * t) * t2**2) * point1[1]
                + ((1 + 2 * t2) * t**2) * point2[1]
                + (num4 * (t2**2)) * num2
                + (num5 * (t**2)) * num3
            )
    return list1
