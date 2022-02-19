from copy import deepcopy
import random
import unittest

from pylib import hstrat


class TestStratumRetentionPredicateDepthProportionalResolution(
    unittest.TestCase,
):

    def test_equality(self):
        assert (
            hstrat.StratumRetentionPredicateDepthProportionalResolution()
            == hstrat.StratumRetentionPredicateDepthProportionalResolution()
        )

        original1 = hstrat.StratumRetentionPredicateDepthProportionalResolution(
            guaranteed_depth_proportional_resolution=10,
        )
        original2 = hstrat.StratumRetentionPredicateDepthProportionalResolution(
            guaranteed_depth_proportional_resolution=42,
        )
        copy1 = deepcopy(original1)
        assert original1 == copy1
        assert original1 != original2
        assert copy1 != original2

    def _do_test_space_complexity(self, guaranteed_depth_proportional_resolution):
        predicate = hstrat.StratumRetentionPredicateDepthProportionalResolution(
            guaranteed_depth_proportional_resolution
                =guaranteed_depth_proportional_resolution,
        )
        column = hstrat.HereditaryStratigraphicColumn(
            stratum_retention_predicate=predicate,
        )

        for generation in range(10000):
            assert (
                column.GetNumStrataRetained()
                <= predicate.CalcNumStrataRetainedUpperBound(
                    num_strata_deposited=column.GetNumStrataDeposited(),
                )
            )
            column.DepositStratum()

    def test_space_complexity(self):
        for guaranteed_depth_proportional_resolution in [
            1,
            2,
            10,
            42,
            97,
        ]:
            self._do_test_space_complexity(
                guaranteed_depth_proportional_resolution,
            )

    def _do_test_resolution(
        self,
        guaranteed_depth_proportional_resolution,
        synchronous,
    ):
        predicate = hstrat.StratumRetentionPredicateDepthProportionalResolution(
            guaranteed_depth_proportional_resolution
                =guaranteed_depth_proportional_resolution,
        )
        column = hstrat.HereditaryStratigraphicColumn(
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
        guaranteed_depth_proportional_resolution,
    ):
        predicate = hstrat.StratumRetentionPredicateDepthProportionalResolution(
            guaranteed_depth_proportional_resolution
                =guaranteed_depth_proportional_resolution,
        )
        column = hstrat.HereditaryStratigraphicColumn(
            stratum_retention_predicate=predicate,
            initial_stratum_annotation=0,
        )

        for generation in range(1,5001):
            for index in range(column.GetNumStrataRetained()):
                assert (
                    column.GetStratumAtColumnIndex(index).GetAnnotation()
                    == column.GetRankAtColumnIndex(index)
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
