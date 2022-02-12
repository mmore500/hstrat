#!/bin/python3

import unittest

from pylib import doubling_search


class TestDoublingSearch(unittest.TestCase):

    def test_doubling_search_trivial(self):
        assert doubling_search(lambda __: True) == 1
        assert doubling_search(lambda __: True, 10) == 10

    def test_doubling_search_nontrivial(self):
        assert doubling_search(lambda x: x >= 5) == 5
        assert doubling_search(lambda x: x >= 5, 10) == 10
        assert doubling_search(lambda x: x >= 422) == 422
        assert doubling_search(lambda x: x >= 422, 10) == 422
        assert doubling_search(lambda x: x >= 423) == 423
        assert doubling_search(lambda x: x >= 423, 10) == 423


if __name__ == '__main__':
    unittest.main()
