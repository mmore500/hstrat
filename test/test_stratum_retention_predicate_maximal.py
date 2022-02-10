#!/bin/python3

import unittest

from pylib import stratum_retention_predicate_maximal

class TestStratumRetentionPredicateMaximal(unittest.TestCase):

    def test(self):
        for column_layers_deposited in range(100):
            for stratum_rank in range(0, column_layers_deposited):
                assert stratum_retention_predicate_maximal(
                    column_layers_deposited=column_layers_deposited,
                    stratum_rank=stratum_rank,
                )

if __name__ == '__main__':
    unittest.main()
