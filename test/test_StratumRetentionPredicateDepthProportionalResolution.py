#!/bin/python3

from copy import deepcopy
import unittest
import random

from pylib import HereditaryStratigraphicColumn
from pylib import StratumRetentionPredicateDepthProportionalResolution

class TestStratumRetentionPredicateDepthProportionalResolution(
    unittest.TestCase,
):

    def test_equality(self):
        assert (
            StratumRetentionPredicateDepthProportionalResolution()
            == StratumRetentionPredicateDepthProportionalResolution()
        )

        original1 = StratumRetentionPredicateDepthProportionalResolution(
            min_intervals_divide_into=10,
        )
        original2 = StratumRetentionPredicateDepthProportionalResolution(
            min_intervals_divide_into=42,
        )
        copy1 = deepcopy(original1)
        assert original1 == copy1
        assert original1 != original2
        assert copy1 != original2


    def _do_test_space_complexity(self, min_intervals_divide_into):
        column = HereditaryStratigraphicColumn(
            stratum_retention_predicate
                =StratumRetentionPredicateDepthProportionalResolution(
                    min_intervals_divide_into=min_intervals_divide_into,
                ),
        )

        for generation in range(10000):
            assert column.GetColumnSize() <= min_intervals_divide_into*2 + 1
            column.DepositLayer()


    def test_space_complexity(self):
        for min_intervals_divide_into in [
            1,
            2,
            10,
            42,
            97,
        ]:
            self._do_test_space_complexity(min_intervals_divide_into)


    def _do_test_resolution(self, min_intervals_divide_into, synchronous,):
        column = HereditaryStratigraphicColumn(
            stratum_retention_predicate
                =StratumRetentionPredicateDepthProportionalResolution(
                    min_intervals_divide_into=min_intervals_divide_into,
                ),
        )

        population = [
            deepcopy(column)
            for __ in range(25)
        ]

        for generation in range(500):

            target_resolu = generation / min_intervals_divide_into

            # subsample consecutive pairs in population
            for f, s in  zip(population, population[1:]):
                assert f.CalcRankOfMrcaUncertaintyWith(s) <= target_resolu
                assert f.CalcRanksSinceMrcaUncertaintyWith(s) <= target_resolu

            random.shuffle(population)
            for target in range(5):
                population[target] = deepcopy(population[-1])
            for individual in population:
                if synchronous or random.choice([True, False]):
                    individual.DepositLayer()


    def test_resolution(self):
        for min_intervals_divide_into in [
            1,
            2,
            10,
            17,
        ]:
            for synchronous in True, False:
                self._do_test_resolution(min_intervals_divide_into, synchronous)


if __name__ == '__main__':
    unittest.main()
