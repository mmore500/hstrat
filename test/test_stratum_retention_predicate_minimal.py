#!/bin/python3

import unittest

from pylib import stratum_retention_predicate_minimal

class TestStratumRetentionPredicateMinimal(unittest.TestCase):

    def test(self):
        for column_layers_deposited in range(100):
            for stratum_rank in range(0, column_layers_deposited):
                assert not stratum_retention_predicate_minimal(
                    column_layers_deposited=column_layers_deposited,
                    stratum_rank=stratum_rank,
                ) or stratum_rank in (0, column_layers_deposited-1,)


if __name__ == '__main__':
    unittest.main()
