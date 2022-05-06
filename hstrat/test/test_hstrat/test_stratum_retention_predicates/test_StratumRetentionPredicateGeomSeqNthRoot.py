from copy import deepcopy
import itertools as it
import random
import unittest

from hstrat import hstrat


class TestStratumRetentionPredicateGeomSeqNthRoot(unittest.TestCase):

    # tests can run independently
    _multiprocess_can_split_ = True

    def _do_test_space_complexity(self, degree, interspersal):
        predicate = hstrat.StratumRetentionPredicateGeomSeqNthRoot(
            degree=degree,
            interspersal=interspersal,
        )
        column = hstrat.HereditaryStratigraphicColumn(
            stratum_retention_predicate=predicate,
        )

        for generation in range(1000):
            assert (
                column.GetNumStrataRetained()
                <= predicate.CalcNumStrataRetainedUpperBound(
                    num_strata_deposited=column.GetNumStrataDeposited(),
                )
            )
            column.DepositStratum()

    def _do_test_resolution(
        self,
        degree,
        interspersal,
        synchronous,
    ):
        test_predicate = hstrat.StratumRetentionPredicateGeomSeqNthRoot(
                degree=degree,
                interspersal=interspersal,
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

    def _do_test_CalcRankAtColumnIndex(
        self,
        degree,
        interspersal,
    ):
        predicate = hstrat.StratumRetentionPredicateGeomSeqNthRoot(
            degree=degree,
            interspersal=interspersal,
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

    def _do_test__get_retained_ranks(
        self,
        degree,
        interspersal,
    ):
        predicate = hstrat.StratumRetentionPredicateGeomSeqNthRoot(
            degree=degree,
            interspersal=interspersal,
        )
        column = hstrat.HereditaryStratigraphicColumn(
            stratum_retention_predicate=predicate,
            initial_stratum_annotation=0,
        )

        for generation in range(1,5001):
            actual_ranks = {
                column.GetStratumAtColumnIndex(index).GetAnnotation()
                for index in range(column.GetNumStrataRetained())
            }
            expected_ranks = predicate._get_retained_ranks(generation)
            assert actual_ranks == expected_ranks
            column.DepositStratum(annotation=generation)

    def test_equality(self):
        assert (
            hstrat.StratumRetentionPredicateGeomSeqNthRoot()
            == hstrat.StratumRetentionPredicateGeomSeqNthRoot()
        )

        original1 = hstrat.StratumRetentionPredicateGeomSeqNthRoot(
            degree=10,
        )
        original2 = hstrat.StratumRetentionPredicateGeomSeqNthRoot(
            degree=42,
        )
        copy1 = deepcopy(original1)
        assert original1 == copy1
        assert original1 != original2
        assert copy1 != original2

    def test_space_complexity(self):
        for degree in [
            1,
            2,
            10,
            42,
            97,
        ]:
            for interspersal in [
                1,
                2,
                5,
            ]:
                self._do_test_space_complexity(
                    degree,
                    interspersal,
                )

    def test_resolution(self):
        for degree in [
            1,
            2,
            4,
        ]:
            for interspersal in [
                1,
                2,
                3,
                5,
            ]:
                for synchronous in True, False:
                    self._do_test_resolution(
                        degree,
                        interspersal,
                        synchronous,
                    )

    def test_CalcRankAtColumnIndex(self):
        for degree in [
            1,
            2,
            10,
            17,
        ]:
            for interspersal in [
                1,
                2,
                5,
            ]:
                self._do_test_CalcRankAtColumnIndex(degree, interspersal)

    def test__get_retained_ranks(self):
        for degree in [
            1,
            2,
            10,
            17,
        ]:
            for interspersal in [
                1,
                2,
                5,
            ]:
                self._do_test__get_retained_ranks(degree, interspersal)


if __name__ == '__main__':
    unittest.main()
