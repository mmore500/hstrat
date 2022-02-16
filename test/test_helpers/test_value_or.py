#!/bin/python3

import unittest

from pylib.helpers import value_or


class TestValueOr(unittest.TestCase):

    def test_with_value(self):

        assert value_or(10, 0) == 10
        assert value_or(False, True) == False
        assert value_or('', 'hello') == ''
        assert value_or(10, 'hello') == 10
        assert value_or(10, None) == 10
        assert value_or(0, None) == 0

    def test_with_none(self):
        assert value_or(None, 0) == 0
        assert value_or(None, True) == True
        assert value_or(None, 'hello') == 'hello'
        assert value_or(None, None) == None


if __name__ == '__main__':
    unittest.main()
