#!/bin/python3

import unittest

from pylib import binary_search

class TestBinarySearch(unittest.TestCase):

    def test_binary_search_singleton(self):
        assert binary_search(lambda __: True, 10, 10) == 10

    def test_binary_search(self):
        assert binary_search(lambda x: x >= 5, 0, 100) == 5

if __name__ == '__main__':
    unittest.main()
