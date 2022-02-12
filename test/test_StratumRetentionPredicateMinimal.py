#!/bin/python3

from copy import deepcopy
import unittest

from pylib import StratumRetentionPredicateMinimal


class TestStratumRetentionPredicateMinimal(unittest.TestCase):

    def test_equality(self):
        assert (
            StratumRetentionPredicateMinimal()
            == StratumRetentionPredicateMinimal()
        )

        original = StratumRetentionPredicateMinimal()
        copy = deepcopy(original)
        assert original == copy

    def test_behavior(self):
        for column_layers_deposited in range(100):
            for stratum_rank in range(0, column_layers_deposited):
                assert not StratumRetentionPredicateMinimal()(
                    column_layers_deposited=column_layers_deposited,
                    stratum_rank=stratum_rank,
                ) or stratum_rank in (0, column_layers_deposited-1,)

    def test_space_complexity(self):
        predicate = StratumRetentionPredicateMinimal()
        column = HereditaryStratigraphicColumn(
            stratum_retention_predicate=predicate,
        )

        for column_layers_deposited in range(100):
            for stratum_rank in range(0, column_layers_deposited):
                upper_bound = predicate.CalcColumnSizeUpperBound(
                    num_layers_deposited=column.GetNumLayersDeposited(),
                )
                assert column.GetColumnSize() <= upper_bound


if __name__ == '__main__':
    unittest.main()
