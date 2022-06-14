from copy import deepcopy
import itertools as it
from more_itertools import zip_equal
import random
import unittest

from hstrat import hstrat
from hstrat import helpers


class TestStratumRetentionPredicateTaperedGeomSeqNthRoot(unittest.TestCase):

    # tests can run independently
    _multiprocess_can_split_ = True

    def _do_test_space_complexity(self, degree, interspersal):
        predicate = hstrat.StratumRetentionPredicateTaperedGeomSeqNthRoot(
            degree=degree,
            interspersal=interspersal,
        )
        column = hstrat.HereditaryStratigraphicColumn(
            stratum_retention_predicate=predicate,
        )

        # MAM passed tests @ 10000 on a4d852
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
        test_predicate = hstrat.StratumRetentionPredicateTaperedGeomSeqNthRoot(
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
        predicate = hstrat.StratumRetentionPredicateTaperedGeomSeqNthRoot(
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
        predicate = hstrat.StratumRetentionPredicateTaperedGeomSeqNthRoot(
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
            assert actual_ranks == expected_ranks, (
                degree,
                interspersal,
                generation,
            )
            column.DepositStratum(annotation=generation)

    def _do_test__calc_common_ratio(self, degree, interspersal):
            predicate = hstrat.StratumRetentionPredicateTaperedGeomSeqNthRoot(
                degree=degree,
                interspersal=interspersal,
            )
            common_ratio_by_generation = [
                predicate._calc_common_ratio(g)
                for g in range(1000)
            ]
            assert helpers.is_nondecreasing(common_ratio_by_generation)

    def _do_test__calc_target_recency(self, degree, interspersal):
            predicate = hstrat.StratumRetentionPredicateTaperedGeomSeqNthRoot(
                degree=degree,
                interspersal=interspersal,
            )
            for pow in range(degree + 1):
                assert helpers.is_nondecreasing(
                    predicate._calc_target_recency(pow, g)
                    for g in range(10000)
                )

    def _do_test__calc_target_rank(self, degree, interspersal):
            predicate = hstrat.StratumRetentionPredicateTaperedGeomSeqNthRoot(
                degree=degree,
                interspersal=interspersal,
            )
            for pow in range(degree + 1):
                assert helpers.is_nondecreasing(
                    predicate._calc_target_rank(pow, g)
                    for g in range(10000)
                )

    def _do_test__calc_rank_cutoff(self, degree, interspersal):
            predicate = hstrat.StratumRetentionPredicateTaperedGeomSeqNthRoot(
                degree=degree,
                interspersal=interspersal,
            )
            for pow in range(degree + 1):
                assert helpers.is_nondecreasing(
                    predicate._calc_rank_cutoff(pow, g)
                    for g in range(10000)
                )

    def _do_test__calc_rank_sep(self, degree, interspersal):
            # is power of 2
            # https://stackoverflow.com/a/57025941
            ispow2 = lambda item: (item & (item-1) == 0) and item
            predicate = hstrat.StratumRetentionPredicateTaperedGeomSeqNthRoot(
                degree=degree,
                interspersal=interspersal,
            )
            for pow in range(degree + 1):
                assert helpers.is_nondecreasing(
                    predicate._calc_rank_sep(pow, g)
                    for g in range(1000)
                )
                assert all(
                    ispow2(predicate._calc_rank_sep(pow, g))
                    for g in range(1000)
                )

    def _do_test__calc_rank_backstop(self, degree, interspersal):
            predicate = hstrat.StratumRetentionPredicateTaperedGeomSeqNthRoot(
                degree=degree,
                interspersal=interspersal,
            )
            for pow in range(degree + 1):
                assert helpers.is_nondecreasing(
                    predicate._calc_rank_backstop(pow, g)
                    for g in range(10000)
                )

    def test_equality(self):
        assert (
            hstrat.StratumRetentionPredicateTaperedGeomSeqNthRoot()
            == hstrat.StratumRetentionPredicateTaperedGeomSeqNthRoot()
        )

        original1 = hstrat.StratumRetentionPredicateTaperedGeomSeqNthRoot(
            degree=10,
        )
        original2 = hstrat.StratumRetentionPredicateTaperedGeomSeqNthRoot(
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

    # generate multiple member functions to enable parallel evaluation
    for degree in [
        1,
        2,
        3,
        9,
        10,
        17,
        101,
    ]:
        for interspersal in [
            1,
            2,
            5,
        ]:
            for synchronous in True, False:
                exec(
                    f'def test_resolution_{degree}_{interspersal}_{synchronous}(self): self._do_test_resolution({degree}, {interspersal}, {synchronous})'
            )

    def test_CalcRankAtColumnIndex(self):
        for degree in [
            1,
            2,
            10,
            17,
            101,
        ]:
            for interspersal in [
                1,
                2,
                5,
            ]:
                self._do_test_CalcRankAtColumnIndex(degree, interspersal)

    # generate multiple member functions to enable parallel evaluation
    for degree in [
        1,
        2,
        3,
        9,
        10,
        17,
        101,
    ]:
        for interspersal in [
            1,
            2,
            5,
        ]:
            exec(
                f'def test__get_retained_ranks_{degree}_{interspersal}(self): self._do_test__get_retained_ranks({degree}, {interspersal})'
            )

    def test__calc_common_ratio(self):
        for degree in [
            1,
            2,
            3,
            9,
            10,
            17,
            101,
        ]:
            for interspersal in [
                1,
                2,
                5,
            ]:
                self._do_test__calc_common_ratio(degree, interspersal)

    def test__calc_target_recency(self):
        for degree in [
            1,
            2,
            3,
            9,
            10,
            17,
            101,
        ]:
            for interspersal in [
                1,
                2,
                5,
            ]:
                self._do_test__calc_target_recency(degree, interspersal)

    def test__calc_target_rank(self):
        for degree in [
            1,
            2,
            3,
            9,
            10,
            17,
            101,
        ]:
            for interspersal in [
                1,
                2,
                5,
            ]:
                self._do_test__calc_target_rank(degree, interspersal)

    def test__calc_rank_cutoff(self):
        for degree in [
            1,
            2,
            3,
            9,
            10,
            17,
            101,
        ]:
            for interspersal in [
                1,
                2,
                5,
            ]:
                self._do_test__calc_rank_cutoff(degree, interspersal)

    def test__calc_rank_sep(self):
        for degree in [
            1,
            2,
            3,
            9,
            10,
            17,
            101,
        ]:
            for interspersal in [
                1,
                2,
                5,
            ]:
                self._do_test__calc_rank_sep(degree, interspersal)

    def test__calc_rank_backstop(self):
        for degree in [
            1,
            2,
            3,
            9,
            10,
            17,
            101,
        ]:
            for interspersal in [
                1,
                2,
                5,
            ]:
                self._do_test__calc_rank_backstop(degree, interspersal)

    def test_first_deposition(self):
        for degree in [
            1,
            2,
            3,
            9,
            10,
            17,
            101,
        ]:
            for interspersal in [
                1,
                2,
                5,
            ]:
                predicate \
                = hstrat.StratumRetentionPredicateTaperedGeomSeqNthRoot(
                    degree=degree,
                    interspersal=interspersal,
                )
                column = hstrat.HereditaryStratigraphicColumn(
                    stratum_retention_predicate=predicate,
                )
                assert column.GetNumStrataDeposited() == 1
                assert column.GetNumStrataRetained() == 1
                assert set(column.GetRetainedRanks()) == {0}
                column.DepositStratum()
                assert column.GetNumStrataDeposited() == 2
                assert column.GetNumStrataRetained() == 2
                assert set(column.GetRetainedRanks()) == {0, 1}

if __name__ == '__main__':
    unittest.main()
