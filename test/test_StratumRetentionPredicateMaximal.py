#!/bin/python3

from copy import deepcopy
import unittest

from pylib import StratumRetentionPredicateMaximal

class TestStratumRetentionPredicateMaximal(unittest.TestCase):

    def test_equality(self):
        assert (
            StratumRetentionPredicateMaximal()
            == StratumRetentionPredicateMaximal()
        )

        original = StratumRetentionPredicateMaximal()
        copy = deepcopy(original)
        assert original == copy

    def test_behavior(self):
        for column_layers_deposited in range(100):
            for stratum_rank in range(0, column_layers_deposited):
                assert StratumRetentionPredicateMaximal()(
                    column_layers_deposited=column_layers_deposited,
                    stratum_rank=stratum_rank,
                )

if __name__ == '__main__':
    unittest.main()
