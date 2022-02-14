#!/bin/python3

from copy import deepcopy
import random
import unittest

from pylib import HereditaryStratigraphicColumn
from pylib import StratumRetentionPredicateFixedResolution

class TestStratumRetentionPredicateFixedResolution(
    unittest.TestCase,
):

    def test_equality(self):
        assert (
            StratumRetentionPredicateFixedResolution()
            == StratumRetentionPredicateFixedResolution()
        )

        original1 = StratumRetentionPredicateFixedResolution(
            fixed_resolution=10,
        )
        original2 = StratumRetentionPredicateFixedResolution(
            fixed_resolution=42,
        )
        copy1 = deepcopy(original1)
        assert original1 == copy1
        assert original1 != original2
        assert copy1 != original2

    def _do_test_space_complexity(self, fixed_resolution):
        predicate = StratumRetentionPredicateFixedResolution(
            fixed_resolution=fixed_resolution,
        )
        column = HereditaryStratigraphicColumn(
            stratum_retention_predicate=predicate,
        )

        for generation in range(500):
            # this particular implementation should return exact number retained
            assert (
                column.GetNumStrataRetained()
                == predicate.CalcNumStrataRetainedUpperBound(
                    num_strata_deposited=column.GetNumStrataDeposited(),
                )
            )
            column.DepositStratum()

    def test_space_complexity(self):
        for fixed_resolution in [
            1,
            2,
            10,
            42,
            97,
        ]:
            self._do_test_space_complexity(
                fixed_resolution,
            )

    def _do_test_resolution(
        self,
        fixed_resolution,
        synchronous,
    ):
        predicate = StratumRetentionPredicateFixedResolution(
            fixed_resolution=fixed_resolution,
        )
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
        for min_intervals_divide_into in [
            1,
            2,
            10,
            17,
        ]:
            for synchronous in True, False:
                self._do_test_resolution(min_intervals_divide_into, synchronous)

    def _do_test_CalcRankAtColumnIndex(
        self,
        fixed_resolution,
    ):
        predicate = StratumRetentionPredicateFixedResolution(
            fixed_resolution=fixed_resolution,
        )
        column = HereditaryStratigraphicColumn(
            stratum_retention_predicate=predicate,
            initial_stratum_annotation=0,
        )

        for generation in range(1,501):
            for index in range(column.GetNumStrataRetained()):
                assert (
                    column.GetStratumAtColumnIndex(index).GetAnnotation()
                    == column.CalcRankAtColumnIndex(index)
                )
            column.DepositStratum(annotation=generation)

    def test_CalcRankAtColumnIndex(self):
        for min_intervals_divide_into in [
            1,
            2,
            10,
            17,
        ]:
            self._do_test_CalcRankAtColumnIndex(min_intervals_divide_into)


if __name__ == '__main__':
    unittest.main()
