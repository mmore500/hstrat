#!/bin/python3

from copy import deepcopy
import unittest
import random

random.seed(1)

from pylib import HereditaryStratigraphicColumn
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
                ) or stratum_rank in (0, column_layers_deposited)

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

    def _do_test_resolution(self, synchronous):
        predicate = StratumRetentionPredicateMinimal()
        column = HereditaryStratigraphicColumn(
            stratum_retention_predicate=predicate,
        )

        population = [
            deepcopy(column)
            for __ in range(25)
        ]

        for generation in range(500):
            # subsample consecutive pairs in population
            for f, s in  zip(population, population[1:]):
                target_resolu = predicate.CalcMrcaUncertaintyUpperBound(
                    first_num_layers_deposited=f.GetNumLayersDeposited(),
                    second_num_layers_deposited=s.GetNumLayersDeposited(),
                )
                assert f.CalcRankOfMrcaUncertaintyWith(s) <= target_resolu
                assert f.CalcRanksSinceMrcaUncertaintyWith(s) <= target_resolu

            random.shuffle(population)
            for target in range(5):
                population[target] = deepcopy(population[-1])
            for individual in population:
                if synchronous or random.choice([True, False]):
                    individual.DepositLayer()

    def test_resolution(self):
        for synchronous in [True, False]:
            self._do_test_resolution(synchronous)


if __name__ == '__main__':
    unittest.main()
