import unittest

from hstrat._auxiliary_lib import is_nondecreasing


class TestIsNondecreasing(unittest.TestCase):

    # tests can run independently
    _multiprocess_can_split_ = True

    def test_empty(self):
        assert is_nondecreasing([])

    def test_singleton(self):
        assert is_nondecreasing(["a"])
        assert is_nondecreasing([0])
        assert is_nondecreasing([1])

    def test_nondecreasing(self):
        assert is_nondecreasing(
            [
                *range(10),
            ]
        )
        assert is_nondecreasing(
            [
                0,
                *range(10),
            ]
        )
        assert is_nondecreasing(
            [
                0,
                0,
                *range(10),
                *range(9, 18),
            ]
        )

    def test_decreasing(self):
        assert not is_nondecreasing(
            [
                0,
                -1,
            ]
        )
        assert not is_nondecreasing(
            [
                *range(10),
                *range(2),
            ]
        )


if __name__ == "__main__":
    unittest.main()
