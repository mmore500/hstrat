#!/bin/python3

import itertools as it
import unittest

from pylib import cyclify


class TestCyclify(unittest.TestCase):

    def test_no_args(self):
        assert list(it.islice(cyclify(), 5)) == []

    def test_one_arg(self):
        assert list(it.islice(cyclify(1), 5)) == [1] * 5
        assert list(it.islice(cyclify('a'), 5)) == ['a'] * 5
        assert list(it.islice(cyclify([]), 5)) == [[]] * 5
        assert list(it.islice(cyclify([1]), 5)) == [[1]] * 5

    def test_two_args(self):
        assert list(it.islice(cyclify(1, 2), 6)) == [1, 2] * 3
        assert list(it.islice(cyclify('a', 1), 6)) == ['a', 1] * 3
        assert list(it.islice(cyclify([], [1]), 6)) == [[], [1]] * 3

if __name__ == '__main__':
    unittest.main()
