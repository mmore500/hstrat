import operator
import unittest

from hstrat._auxiliary_lib import find_bounds


class TestFindBounds(unittest.TestCase):

    # tests can run independently
    _multiprocess_can_split_ = True

    def test_empty(self):
        assert find_bounds(
            query=5,
            iterable=iter(()),
        ) == (None, None)

    def test_singleton_above(self):
        assert find_bounds(
            query=5,
            iterable=(7,),
        ) == (None, 7)

    def test_singleton_below(self):
        assert find_bounds(
            query=5,
            iterable=(0,),
        ) == (0, None)

    def test_singleton_equal(self):
        assert find_bounds(
            query=5,
            iterable=(5,),
        ) == (None, None)

    def test_doublet_equal(self):
        assert find_bounds(
            query=5,
            iterable=(5, 5),
        ) == (None, None)

    def test_doublet_above(self):
        assert find_bounds(
            query=5,
            iterable=(8, 7),
        ) == (None, 7)

    def test_doublet_below(self):
        assert find_bounds(
            query=5,
            iterable=(-10, -1),
        ) == (-1, None)

    def test_doublet_split(self):
        assert find_bounds(
            query=5,
            iterable=(8, -1),
        ) == (-1, 8)
        assert find_bounds(
            query=5,
            iterable=(-1, 8),
        ) == (-1, 8)

    def test_long_with_edgecases(self):
        assert find_bounds(
            query=5,
            iterable=(8, 8, 5, -1, 7, -1, -10, 0, 5, 5, 20, 3, 3, 6, 100),
        ) == (3, 6)

    def test_key(self):
        assert find_bounds(
            query=5,
            iterable=(8, 8, 5, -1, 7, -1, -10, 0, 5, 5, 20, 3, 3, 6, 100),
            key=lambda x: -x,
        ) == (1, 10)

    def test_initializer(self):
        assert find_bounds(
            query=5,
            iterable=(8, 8, 5, -1, 7, -1, -10, 0, 5, 5, 20, 3, 3, 6, 100),
            initializer=(None, 7),
        ) == (3, 6)
        assert find_bounds(
            query=5,
            iterable=(8, 8, 5, -1, 7, -1, -10, 0, 5, 5, 20, 3, 3, 6, 100),
            initializer=(4, 7),
        ) == (4, 6)
        assert find_bounds(
            query=5,
            iterable=(8, 8, 5, -1, 7, -1, -10, 0, 5, 5, 20, 3, 3, 6, 100),
            initializer=(4, None),
        ) == (4, 6)
        assert find_bounds(
            query=5, iterable=(8, 8, 5, 7, 20, 6, 100), initializer=(4, None)
        ) == (4, 6)

    def test_filter_above(self):
        assert find_bounds(
            query=5,
            iterable=(8, 8, 5, -1, 7, -1, -10, 0, 5, 5, 20, 3, 3, 6, 100),
            filter_above=operator.ge,
        ) == (3, 5)

    def test_filter_below(self):
        assert find_bounds(
            query=5,
            iterable=(8, 8, 5, -1, 7, -1, -10, 0, 5, 5, 20, 3, 3, 6, 100),
            filter_below=operator.le,
        ) == (5, 6)

    def test_filter_abovebelow(self):
        assert find_bounds(
            query=5,
            iterable=(8, 8, 5, -1, 7, -1, -10, 0, 5, 5, 20, 3, 3, 6, 100),
            filter_above=operator.ge,
            filter_below=operator.le,
        ) == (5, 5)


if __name__ == "__main__":
    unittest.main()
