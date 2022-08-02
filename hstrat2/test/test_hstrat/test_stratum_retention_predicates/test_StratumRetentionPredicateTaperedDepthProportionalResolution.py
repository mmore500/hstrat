from copy import deepcopy
import random
import unittest

from hstrat import hstrat


class TestStratumRetentionPredicateTaperedDepthProportionalResolution(
    unittest.TestCase,
):

    # tests can run independently
    _multiprocess_can_split_ = True

    def test_equality(self):
        assert (
            hstrat.StratumRetentionPredicateTaperedDepthProportionalResolution()
            ==
            hstrat.StratumRetentionPredicateTaperedDepthProportionalResolution()
        )

        original1 \
           = hstrat.StratumRetentionPredicateTaperedDepthProportionalResolution(
            guaranteed_depth_proportional_resolution=10,
        )
        original2 \
           = hstrat.StratumRetentionPredicateTaperedDepthProportionalResolution(
            guaranteed_depth_proportional_resolution=42,
        )
        copy1 = deepcopy(original1)
        assert original1 == copy1
        assert original1 != original2
        assert copy1 != original2

    def _do_test_space_complexity(
        self,
        guaranteed_depth_proportional_resolution
    ):
        predicate \
           = hstrat.StratumRetentionPredicateTaperedDepthProportionalResolution(
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
            assert (
                column.GetNumStrataRetained()
                == predicate.CalcNumStrataRetainedExact(
                    num_strata_deposited=column.GetNumStrataDeposited(),
                )
            ), (
                guaranteed_depth_proportional_resolution,
                column.GetNumStrataDeposited(),
                column.GetNumStrataRetained(),
                predicate.CalcNumStrataRetainedExact(
                    num_strata_deposited=column.GetNumStrataDeposited(),
                ),
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
        predicate \
          = hstrat.StratumRetentionPredicateTaperedDepthProportionalResolution(
            guaranteed_depth_proportional_resolution
                =guaranteed_depth_proportional_resolution,
        )
        column = hstrat.HereditaryStratigraphicColumn(
            stratum_retention_predicate=predicate,
        )

        population = [
            column.Clone()
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
                population[target] = population[-1].Clone()
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
        predicate \
           = hstrat.StratumRetentionPredicateTaperedDepthProportionalResolution(
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

    def _do_test_CalcRankAtColumnIndex(
        self,
        guaranteed_depth_proportional_resolution,
    ):
        test_predicate \
           = hstrat.StratumRetentionPredicateTaperedDepthProportionalResolution(
                guaranteed_depth_proportional_resolution
                    =guaranteed_depth_proportional_resolution,
            )
        test_column = hstrat.HereditaryStratigraphicColumn(
            always_store_rank_in_stratum=True,
            stratum_ordered_store_factory
                =hstrat.HereditaryStratumOrderedStoreDict,
            stratum_retention_predicate=test_predicate,
        )

        for i in range(10000):
            test_column.DepositStratum()
            actual_ranks = { *test_column.GetRetainedRanks() }
            calcualted_ranks = {
                test_predicate.CalcRankAtColumnIndex(
                    index=i,
                    num_strata_deposited=test_column.GetNumStrataDeposited()
                )
                for i in range(test_column.GetNumStrataRetained())
            }
            assert actual_ranks == calcualted_ranks
            # in-progress deposition case
            assert test_predicate.CalcRankAtColumnIndex(
                index=test_column.GetNumStrataRetained(),
                num_strata_deposited=test_column.GetNumStrataDeposited(),
            ) == test_column.GetNumStrataDeposited()

    def test_CalcRankAtColumnIndex(self):
        for guaranteed_depth_proportional_resolution in [
            1,
            2,
            3,
            7,
            42,
            100,
        ]:
            self._do_test_CalcRankAtColumnIndex(
                guaranteed_depth_proportional_resolution,
            )


if __name__ == '__main__':
    unittest.main()
