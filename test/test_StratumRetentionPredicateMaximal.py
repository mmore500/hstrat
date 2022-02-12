#!/bin/python3

from copy import deepcopy
import unittest
import random

random.seed(1)

from pylib import HereditaryStratigraphicColumn
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

    def _do_test_resolution(self, synchronous):
        predicate = StratumRetentionPredicateMaximal()
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
