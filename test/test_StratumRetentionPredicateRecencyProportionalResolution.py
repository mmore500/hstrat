#!/bin/python3

from copy import deepcopy
import itertools as it
import random
import unittest

random.seed(1)

from pylib import HereditaryStratigraphicColumn
from pylib import HereditaryStratigraphicColumnBundle
from pylib import StratumRetentionPredicateMaximal
from pylib import StratumRetentionPredicateRecencyProportionalResolution


class TestStratumRetentionPredicateRecencyProportionalResolution(
    unittest.TestCase,
):

    def test_equality(self):
        assert (
            StratumRetentionPredicateRecencyProportionalResolution()
            == StratumRetentionPredicateRecencyProportionalResolution()
        )

        original1 = StratumRetentionPredicateRecencyProportionalResolution(
            guaranteed_mrca_recency_proportional_resolution=2,
        )
        original2 = StratumRetentionPredicateRecencyProportionalResolution(
            guaranteed_mrca_recency_proportional_resolution=3,
        )
        copy1 = deepcopy(original1)
        assert original1 == copy1
        assert original1 != original2
        assert copy1 != original2

    def _do_test_space_complexity(
        self,
        guaranteed_mrca_recency_proportional_resolution,
    ):
        predicate = StratumRetentionPredicateRecencyProportionalResolution(
            guaranteed_mrca_recency_proportional_resolution
                =guaranteed_mrca_recency_proportional_resolution,
        )
        column = HereditaryStratigraphicColumn(
            stratum_retention_predicate=predicate,
        )

        for generation in range(1000):
            assert (
                column.GetNumStrataRetained()
                <= predicate.CalcNumStrataRetainedUpperBound(generation)
            )


    def test_space_complexity(self):
        for guaranteed_mrca_recency_proportional_resolution in [
            2,
            10,
            42,
        ]:
            self._do_test_space_complexity(
                guaranteed_mrca_recency_proportional_resolution,
            )


    def _do_test_resolution(
        self,
        guaranteed_mrca_recency_proportional_resolution,
        synchronous,
    ):
        test_predicate = StratumRetentionPredicateRecencyProportionalResolution(
            guaranteed_mrca_recency_proportional_resolution
                =guaranteed_mrca_recency_proportional_resolution,
        )
        column_test = HereditaryStratigraphicColumn(
            stratum_retention_predicate=test_predicate,
        )
        column_control = HereditaryStratigraphicColumn(
            stratum_retention_predicate=StratumRetentionPredicateMaximal(),
        )

        column_bundle = HereditaryStratigraphicColumnBundle({
            'test' : column_test,
            'control' : column_control,
        })

        population = [
            deepcopy(column_bundle)
            for __ in range(25)
        ]
        forked_population = [
            deepcopy(column_bundle)
            for __ in range(5)
        ]
        ancestor = [ deepcopy(column_bundle) ]

        for generation in range(500):
            # subsample consecutive pairs in population
            for f, s in it.chain(
                zip(population, population[1:]),
                zip(forked_population, population),
                zip(population, forked_population),
                zip(ancestor, population),
                zip(population, ancestor),
            ):

                actual_rank_of_mrca = (
                    f['control'].CalcRankOfLastCommonalityWith(s['control'])
                )
                assert (
                    f['control'].CalcRankOfMrcaUncertaintyWith(s['control'])
                    == 0
                )

                target_resolu = test_predicate.CalcMrcaUncertaintyUpperBound(
                    actual_rank_of_mrca=actual_rank_of_mrca,
                    first_num_strata_deposited=f.GetNumStrataDeposited(),
                    second_num_strata_deposited=s.GetNumStrataDeposited(),
                )

                assert (
                    f['test'].CalcRankOfMrcaUncertaintyWith(s['test'])
                    <= target_resolu
                )
                assert (
                    s['test'].CalcRankOfMrcaUncertaintyWith(f['test'])
                    <= target_resolu
                )
                assert (
                    f['test'].CalcRanksSinceMrcaUncertaintyWith(s['test'])
                    <= target_resolu
                )
                assert (
                    s['test'].CalcRanksSinceMrcaUncertaintyWith(f['test'])
                    <= target_resolu
                )

            random.shuffle(population)
            random.shuffle(forked_population)
            # reproduction
            for target in range(5):
                population[target] = deepcopy(population[-1])
            # advance generations
            for individual in it.chain(
                iter(population),
                iter(forked_population),
            ):
                if synchronous or random.choice([True, False]):
                    individual.DepositStratum()

    def test_resolution(self):
        for guaranteed_mrca_recency_proportional_resolution in [
            2,
            3,
            17,
            100,
        ]:
            for synchronous in True, False:
                self._do_test_resolution(
                    guaranteed_mrca_recency_proportional_resolution,
                    synchronous,
                )


if __name__ == '__main__':
    unittest.main()
