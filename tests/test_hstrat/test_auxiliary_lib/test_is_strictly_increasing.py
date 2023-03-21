import unittest

from hstrat._auxiliary_lib import is_strictly_increasing


class TestIsStrictlyIncreasing(unittest.TestCase):

    # tests can run independently
    _multiprocess_can_split_ = True

    def test_empty(self):
        assert is_strictly_increasing([])

    def test_singleton(self):
        assert is_strictly_increasing(["a"])
        assert is_strictly_increasing([0])
        assert is_strictly_increasing([1])

    def test_nonincreasing(self):
        assert is_strictly_increasing(
            [
                *range(10),
            ]
        )
        assert not is_strictly_increasing(
            [
                0,
                *range(10),
            ]
        )
        assert not is_strictly_increasing(
            [
                0,
                0,
                *range(10),
                *range(9, 18),
            ]
        )

    def test_decreasing(self):
        assert not is_strictly_increasing(
            [
                0,
                -1,
            ]
        )
        assert not is_strictly_increasing(
            [
                *range(10),
                *range(2),
            ]
        )

    def test_increasing(self):
        assert is_strictly_increasing(
            [
                -1,
                0,
            ]
        )
        assert is_strictly_increasing(range(10))
        assert is_strictly_increasing([(-1, 0.0), (0, -2), (0, -1)])


if __name__ == "__main__":
    unittest.main()
