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
        for column_strata_deposited in range(100):
            for stratum_rank in range(0, column_strata_deposited):
                assert not StratumRetentionPredicateMinimal()(
                    column_strata_deposited=column_strata_deposited,
                    stratum_rank=stratum_rank,
                ) or stratum_rank in (0, column_strata_deposited)

    def test_space_complexity(self):
        predicate = StratumRetentionPredicateMinimal()
        column = HereditaryStratigraphicColumn(
            stratum_retention_predicate=predicate,
        )

        for column_strata_deposited in range(100):
            for stratum_rank in range(0, column_strata_deposited):
                upper_bound = predicate.CalcNumStrataRetainedUpperBound(
                    num_strata_deposited=column.GetNumStrataDeposited(),
                )
                assert column.GetNumStrataRetained() <= upper_bound

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
                    first_num_strata_deposited=f.GetNumStrataDeposited(),
                    second_num_strata_deposited=s.GetNumStrataDeposited(),
                )
                assert f.CalcRankOfMrcaUncertaintyWith(s) <= target_resolu
                assert f.CalcRanksSinceMrcaUncertaintyWith(s) <= target_resolu

            random.shuffle(population)
            for target in range(5):
                population[target] = deepcopy(population[-1])
            for individual in population:
                if synchronous or random.choice([True, False]):
                    individual.DepositStratum()

    def test_resolution(self):
        for synchronous in [True, False]:
            self._do_test_resolution(synchronous)


if __name__ == '__main__':
    unittest.main()
