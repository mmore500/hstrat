#!/bin/python3

from copy import deepcopy
import unittest

from pylib import StratumRetentionPredicateStochastic


class TestStratumRetentionPredicateStochastic(unittest.TestCase):

    def test_equality(self):
        assert (
            StratumRetentionPredicateStochastic()
            == StratumRetentionPredicateStochastic()
        )

        original = StratumRetentionPredicateStochastic()
        copy = deepcopy(original)
        assert original == copy


if __name__ == '__main__':
    unittest.main()
