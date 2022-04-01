from copy import deepcopy
from iterify import cyclify
import itertools as it
import random
import unittest

random.seed(1)

from hstrat import hstrat


class TestStratumRetentionPredicateSpaceFillApproxRecencyProportionalResolution(
    unittest.TestCase,
):

    # tests can run independently
    _multiprocess_can_split_ = True

    def test_equality(self):
        assert (
            hstrat.StratumRetentionPredicateSpaceFillApproxRecencyProportionalResolution()
            == hstrat.StratumRetentionPredicateSpaceFillApproxRecencyProportionalResolution()
        )

        original1 \
            = hstrat.StratumRetentionPredicateSpaceFillApproxRecencyProportionalResolution(
                target_size=8,
        )
        original2 \
            = hstrat.StratumRetentionPredicateSpaceFillApproxRecencyProportionalResolution(
                target_size=9,
        )
        copy1 = deepcopy(original1)
        assert original1 == copy1
        assert original1 != original2
        assert copy1 != original2

    def _do_test_space_complexity(
        self,
        target_size,
    ):
        predicate = \
            hstrat.StratumRetentionPredicateSpaceFillApproxRecencyProportionalResolution(
                target_size=target_size,
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
        for target_size in [
            8,
            17,
            100,
        ]:
            self._do_test_space_complexity(
                target_size,
            )


    def _do_test_resolution(
        self,
        target_size,
        synchronous,
    ):
        test_predicate = \
            hstrat.StratumRetentionPredicateSpaceFillApproxRecencyProportionalResolution(
                target_size=target_size,
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
        for target_size in [
            8,
            17,
            100,
        ]:
            for synchronous in True, False:
                self._do_test_resolution(
                    target_size,
                    synchronous,
                )

    def _do_test_deep_resolution(
        self,
        target_size,
    ):
        test_predicate = \
            hstrat.StratumRetentionPredicateSpaceFillApproxRecencyProportionalResolution(
                target_size=target_size,
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
        for target_size in [
            8,
            17,
            100,
        ]:
            self._do_test_deep_resolution(
                target_size,
            )

    def _do_test_deep_space_complexity(
        self,
        target_size,
    ):
        test_predicate = \
            hstrat.StratumRetentionPredicateSpaceFillApproxRecencyProportionalResolution(
                target_size=target_size,
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
        for target_size in [
            8,
            17,
            100,
        ]:
            self._do_test_deep_space_complexity(
                target_size,
            )


if __name__ == '__main__':
    unittest.main()
