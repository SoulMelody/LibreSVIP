def interpolate_akima(x: list[float], y: list[float], x_new: list[int]) -> list[float]:
    """translated to pure python from https://github.com/cgohlke/akima"""
    n = len(x)

    # Validation
    if n < 3:
        msg = "Data points too small"
        raise ValueError(msg)

    dx = [x[i + 1] - x[i] for i in range(n - 1)]
    if any(d <= 0 for d in dx):
        msg = "X must be monotonically increasing"
        raise ValueError(msg)

    # Differences
    m = [(y[i + 1] - y[i]) / dx[i] for i in range(n - 1)]

    mm = 2.0 * m[0] - m[1]
    mmm = 2.0 * mm - m[0]
    mp = 2.0 * m[n - 2] - m[n - 3]
    mpp = 2.0 * mp - m[n - 2]

    m1 = [mmm, mm, *m, mp, mpp]

    # Slope estimates
    dm = [abs(m1[i + 1] - m1[i]) for i in range(len(m1) - 1)]
    f1, f2 = dm[2 : n + 2], dm[:n]
    f12 = [f1[i] + f2[i] for i in range(n)]

    # Detect almost equal slopes
    ids = [i for i in range(n - 1) if f12[i] > 1e-9 * max(f12)]
    b = m1[1 : n + 1]

    for i in ids:
        b[i] = (f1[i] * m1[i + 1] + f2[i] * m1[i + 2]) / f12[i]

    c = [(3 * m[i] - 2 * b[i] - b[i + 1]) / dx[i] for i in range(n - 1)]
    d = [(b[i] + b[i + 1] - 2 * m[i]) / dx[i] ** 2 for i in range(n - 1)]

    bins = [0] * len(x_new)
    for j, val in enumerate(x_new):
        idx = 0
        while idx < n - 1 and x[idx] <= val:
            idx += 1
        bins[j] = idx - 1

    bb = bins
    wj = [x_new[j] - x[bb[j]] for j in range(len(x_new))]

    return [
        ((wj[j] * d[bb[j]] + c[bb[j]]) * wj[j] + b[bb[j]]) * wj[j] + y[bb[j]]
        for j in range(len(x_new))
    ]
