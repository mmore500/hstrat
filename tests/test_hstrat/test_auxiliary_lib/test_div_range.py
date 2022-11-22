import unittest

from hstrat._auxiliary_lib import div_range


class TestDivRange(unittest.TestCase):

    # tests can run independently
    _multiprocess_can_split_ = True

    def test_empty(self):

        assert [*div_range(10, 12, 2)] == []
        assert [*div_range(10, 10, 2)] == []

    def test_singleton(self):

        assert [*div_range(10, 8, 2)] == [10]

    def test_several(self):

        assert [*div_range(10, 1, 2)] == [10, 5, 2]


if __name__ == "__main__":
    unittest.main()
