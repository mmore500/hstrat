import itertools as it
import unittest

from pylib.helpers import iterify


class TestCyclify(unittest.TestCase):

    def test_no_args(self):
        assert list(iterify()) == []

    def test_one_arg(self):
        assert list(iterify(1)) == [1]
        assert list(iterify('a')) == ['a']
        assert list(iterify([])) == [[]]
        assert list(iterify([1])) == [[1]]

    def test_two_args(self):
        assert list(iterify(1, 2)) == [1, 2]
        assert list(iterify('a', 1)) == ['a', 1]
        assert list(iterify([], [1])) == [[], [1]]

if __name__ == '__main__':
    unittest.main()
