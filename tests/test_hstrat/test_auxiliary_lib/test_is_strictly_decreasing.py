import unittest

from hstrat._auxiliary_lib import is_strictly_decreasing


class TestIsStrictlyDecreasing(unittest.TestCase):

    # tests can run independently
    _multiprocess_can_split_ = True

    def test_empty(self):
        assert is_strictly_decreasing([])

    def test_singleton(self):
        assert is_strictly_decreasing(["a"])
        assert is_strictly_decreasing([0])
        assert is_strictly_decreasing([1])

    def test_nondecreasing(self):
        assert is_strictly_decreasing(
            reversed(
                [
                    *range(10),
                ]
            )
        )
        assert not is_strictly_decreasing(
            reversed(
                [
                    0,
                    *range(10),
                ]
            )
        )
        assert not is_strictly_decreasing(
            reversed(
                [
                    0,
                    0,
                    *range(10),
                    *range(9, 18),
                ]
            )
        )

    def test_decreasing(self):
        assert not is_strictly_decreasing(
            [
                -1,
                0,
            ]
        )
        assert not is_strictly_decreasing(
            reversed(
                [
                    *range(10),
                    *range(2),
                ]
            )
        )


if __name__ == "__main__":
    unittest.main()
