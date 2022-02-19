import unittest

from pylib.helpers import binary_search


class TestBinarySearch(unittest.TestCase):

    def test_binary_search_singleton(self):
        assert binary_search(lambda __: True, 10, 10) == 10

    def test_binary_search(self):
        assert binary_search(lambda x: x >= 5, 0, 100) == 5

    def test_fruitless_binary_search(self):
        assert binary_search(lambda x: False, 0, 100) == None

if __name__ == '__main__':
    unittest.main()
