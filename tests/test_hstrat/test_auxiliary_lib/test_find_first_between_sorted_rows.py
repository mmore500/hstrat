import numpy as np

from hstrat._auxiliary_lib import find_first_between_sorted_rows


def test_find_first_between_sorted_rows():
    rng = np.random.default_rng(1)
    rows = np.sort(rng.integers(0, 100, size=(500, 16)), axis=1)
    rows = rows.astype(np.float64)
    after = rng.integers(-5, 105, size=500).astype(np.float64)
    before = after + rng.integers(0, 60, size=500)
    for num in [1, 2, 20]:
        result = find_first_between_sorted_rows(rows, after, before, num)
        for row, a, b, res in zip(rows, after, before, result):
            between = [r for r in row if a < r < b][:num]
            expected = between + [np.inf] * (num - len(between))
            assert res.tolist() == expected
