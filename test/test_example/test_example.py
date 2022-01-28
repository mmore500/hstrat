#!/bin/python3

import unittest

from pylib.example import example

class TestExample(unittest.TestCase):

    def test_example(self):
        example()

if __name__ == '__main__':
    unittest.main()
