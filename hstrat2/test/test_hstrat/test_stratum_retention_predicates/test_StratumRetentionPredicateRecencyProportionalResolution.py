from copy import deepcopy
from iterify import cyclify
import itertools as it
import random
import unittest

random.seed(1)

from hstrat import hstrat


class TestStratumRetentionPredicateRecencyProportionalResolution(
    unittest.TestCase,
):

    # tests can run independently
    _multiprocess_can_split_ = True

    def test_equality(self):
        assert (
            hstrat.StratumRetentionPredicateRecencyProportionalResolution()
            == hstrat.StratumRetentionPredicateRecencyProportionalResolution()
        )

        original1 \
            = hstrat.StratumRetentionPredicateRecencyProportionalResolution(
                guaranteed_mrca_recency_proportional_resolution=2,
        )
        original2 \
            = hstrat.StratumRetentionPredicateRecencyProportionalResolution(
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
        predicate = \
            hstrat.StratumRetentionPredicateRecencyProportionalResolution(
                guaranteed_mrca_recency_proportional_resolution
                    =guaranteed_mrca_recency_proportional_resolution,
        )
        column = hstrat.HereditaryStratigraphicColumn(
            stratum_retention_predicate=predicate,
            stratum_ordered_store_factory
                =hstrat.HereditaryStratumOrderedStoreList,
        )

        for generation in range(1, 1000):
            target_space = predicate.CalcNumStrataRetainedExact(generation)
            assert target_space == column.GetNumStrataRetained()
            column.DepositStratum()

    def test_space_complexity(self):
        for guaranteed_mrca_recency_proportional_resolution in [
            0,
            1,
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
        test_predicate = \
            hstrat.StratumRetentionPredicateRecencyProportionalResolution(
                guaranteed_mrca_recency_proportional_resolution
                    =guaranteed_mrca_recency_proportional_resolution,
        )
        column_test = hstrat.HereditaryStratigraphicColumn(
            stratum_ordered_store_factory
                =hstrat.HereditaryStratumOrderedStoreList,
            stratum_retention_predicate=test_predicate,
        )
        column_control = hstrat.HereditaryStratigraphicColumn(
            stratum_ordered_store_factory
                =hstrat.HereditaryStratumOrderedStoreList,
            stratum_retention_condemner
                =hstrat.StratumRetentionCondemnerPerfectResolution(),
        )

        column_bundle = hstrat.HereditaryStratigraphicColumnBundle({
            'test' : column_test,
            'control' : column_control,
        })

        population = [
            column_bundle.Clone()
            for __ in range(25)
        ]
        forked_population = [
            column_bundle.Clone()
            for __ in range(5)
        ]
        ancestor = [ column_bundle.Clone() ]

        for generation in range(500):
            # subsample consecutive pairs in population
            for f, s in it.chain(
                zip(population, population[1:]),
                zip(forked_population, population),
                zip(population, forked_population),
                zip(ancestor, population),
                zip(population, ancestor),
            ):

                actual_rank_of_mrca \
                    = f['control'].CalcRankOfLastRetainedCommonalityWith(
                        s['control']
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
                population[target] = population[-1].Clone()
            # advance generations
            for individual in it.chain(
                iter(population),
                iter(forked_population),
            ):
                if synchronous or random.choice([True, False]):
                    individual.DepositStratum()

    def test_resolution(self):
        for guaranteed_mrca_recency_proportional_resolution in [
            0,
            1,
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

    def _do_test_resolution_regression_case(
        self,
        actual_rank_of_mrca,
        guaranteed_mrca_recency_proportional_resolution,
        num_strata_deposited,
    ):
        test_predicate = \
            hstrat.StratumRetentionPredicateRecencyProportionalResolution(
                guaranteed_mrca_recency_proportional_resolution
                    =guaranteed_mrca_recency_proportional_resolution,
        )
        first = hstrat.HereditaryStratigraphicColumn(
            stratum_ordered_store_factory
                =hstrat.HereditaryStratumOrderedStoreDict,
            stratum_retention_predicate=test_predicate,
        )

        for __ in range(actual_rank_of_mrca): first.DepositStratum()

        second = first.Clone()

        first_num_strata, second_num_strata = num_strata_deposited
        for __ in range(first_num_strata - actual_rank_of_mrca):
            first.DepositStratum()
        for __ in range(second_num_strata - actual_rank_of_mrca):
            second.DepositStratum()

        target_resolution = test_predicate.CalcMrcaUncertaintyUpperBound(
            actual_rank_of_mrca=actual_rank_of_mrca,
            first_num_strata_deposited=first.GetNumStrataDeposited(),
            second_num_strata_deposited=second.GetNumStrataDeposited(),
        )

        assert (
            second.CalcRankOfMrcaUncertaintyWith(first)
            <= target_resolution
        )
        assert (
            first.CalcRanksSinceMrcaUncertaintyWith(second)
            <= target_resolution
        )
        assert (
            second.CalcRanksSinceMrcaUncertaintyWith(first)
            <= target_resolution
        )

    def test_resolution_regression(self):
        for case in [
            {
                'actual_rank_of_mrca' : 111,
                'guaranteed_mrca_recency_proportional_resolution' : 17,
                'num_strata_deposited' : (148, 152),
            },
            {
                'actual_rank_of_mrca' : 101,
                'guaranteed_mrca_recency_proportional_resolution' : 17,
                'num_strata_deposited' : (144, 144),
            },
            {
                'actual_rank_of_mrca' : 103,
                'guaranteed_mrca_recency_proportional_resolution' : 17,
                'num_strata_deposited' : (144, 144),
            },
        ]:
            self._do_test_resolution_regression_case(**case)

    def _do_test_deep_resolution(
        self,
        guaranteed_mrca_recency_proportional_resolution,
    ):
        test_predicate = \
            hstrat.StratumRetentionPredicateRecencyProportionalResolution(
                guaranteed_mrca_recency_proportional_resolution
                    =guaranteed_mrca_recency_proportional_resolution,
        )
        column_test = hstrat.HereditaryStratigraphicColumn(
            stratum_ordered_store_factory
                =hstrat.HereditaryStratumOrderedStoreDict,
            stratum_retention_predicate=test_predicate,
        )
        column_control = hstrat.HereditaryStratigraphicColumn(
            stratum_ordered_store_factory
                =hstrat.HereditaryStratumOrderedStoreList,
            stratum_retention_condemner
                =hstrat.StratumRetentionCondemnerPerfectResolution(),
        )

        individual = hstrat.HereditaryStratigraphicColumnBundle({
            'test' : column_test,
            'control' : column_control,
        })

        snapshots = [individual]
        for snapshot in range(100):
                for fastforward in range(100):
                        individual.DepositStratum()
                snapshots.append(individual.Clone())


        for f, s in it.chain(
            zip(cyclify(individual), snapshots),
            zip(snapshots, cyclify(individual)),
        ):
            actual_rank_of_mrca = (
                f['control'].CalcRankOfLastRetainedCommonalityWith(s['control'])
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

    def test_deep_resolution(self):
        for guaranteed_mrca_recency_proportional_resolution in [
            0,
            1,
            2,
            3,
            17,
            100,
        ]:
            self._do_test_deep_resolution(
                guaranteed_mrca_recency_proportional_resolution,
            )

    def _do_test_deep_space_complexity(
        self,
        guaranteed_mrca_recency_proportional_resolution,
    ):
        test_predicate = \
            hstrat.StratumRetentionPredicateRecencyProportionalResolution(
                guaranteed_mrca_recency_proportional_resolution
                    =guaranteed_mrca_recency_proportional_resolution,
            )
        individual = hstrat.HereditaryStratigraphicColumn(
            stratum_ordered_store_factory
                =hstrat.HereditaryStratumOrderedStoreDict,
            stratum_retention_predicate=test_predicate,
        )

        snapshots = [individual]
        for snapshot in range(100):
                for fastforward in range(100):
                        individual.DepositStratum()
                snapshots.append(individual.Clone())


        for snapshot in snapshots:
            target_space = test_predicate.CalcNumStrataRetainedExact(
                num_strata_deposited=snapshot.GetNumStrataDeposited(),
            )
            # implementation provides an exact count of num retained
            assert snapshot.GetNumStrataRetained() == target_space

    def test_deep_space_complexity(self):
        for guaranteed_mrca_recency_proportional_resolution in [
            1,
            2,
            3,
            17,
            100,
        ]:
            self._do_test_deep_space_complexity(
                guaranteed_mrca_recency_proportional_resolution,
            )


if __name__ == '__main__':
    unittest.main()
