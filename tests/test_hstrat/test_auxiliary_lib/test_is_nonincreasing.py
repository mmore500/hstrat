import unittest

from hstrat._auxiliary_lib import is_nonincreasing


class TestIsNonincreasing(unittest.TestCase):

    # tests can run independently
    _multiprocess_can_split_ = True

    def test_empty(self):
        assert is_nonincreasing([])

    def test_singleton(self):
        assert is_nonincreasing(["a"])
        assert is_nonincreasing([0])
        assert is_nonincreasing([1])

    def test_nondecreasing(self):
        assert is_nonincreasing(
            reversed(
                [
                    *range(10),
                ]
            )
        )
        assert is_nonincreasing(
            reversed(
                [
                    0,
                    *range(10),
                ]
            )
        )
        assert is_nonincreasing(
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
        assert not is_nonincreasing(
            [
                -1,
                0,
            ]
        )
        assert not is_nonincreasing(
            reversed(
                [
                    *range(10),
                    *range(2),
                ]
            )
        )


if __name__ == "__main__":
    unittest.main()
