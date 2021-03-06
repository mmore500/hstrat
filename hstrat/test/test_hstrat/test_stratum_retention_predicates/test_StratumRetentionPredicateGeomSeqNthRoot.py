from copy import deepcopy
import itertools as it
from more_itertools import zip_equal
import random
import unittest

from hstrat import hstrat
from hstrat import helpers


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

    def _do_test__calc_common_ratio(self, degree, interspersal):
            predicate = hstrat.StratumRetentionPredicateGeomSeqNthRoot(
                degree=degree,
                interspersal=interspersal,
            )
            common_ratio_by_generation = [
                predicate._calc_common_ratio(g)
                for g in range(1000)
            ]
            assert helpers.is_nondecreasing(common_ratio_by_generation)

    def _do_test__iter_target_recencies(self, degree, interspersal):
            predicate = hstrat.StratumRetentionPredicateGeomSeqNthRoot(
                degree=degree,
                interspersal=interspersal,
            )
            target_recencies_by_generation = [
                predicate._iter_target_recencies(g)
                for g in range(10000)
            ]
            zipped = list(zip_equal(*target_recencies_by_generation))
            assert len(zipped) == degree
            for equiv_seq in zipped:
                assert helpers.is_nondecreasing(equiv_seq)

    def _do_test__iter_target_ranks(self, degree, interspersal):
            predicate = hstrat.StratumRetentionPredicateGeomSeqNthRoot(
                degree=degree,
                interspersal=interspersal,
            )
            target_ranks_by_generation = [
                predicate._iter_target_ranks(g)
                for g in range(10000)
            ]
            zipped = list(zip_equal(*target_ranks_by_generation))
            assert len(zipped) == degree
            for equiv_seq in zipped:
                assert helpers.is_nondecreasing(equiv_seq)

    def _do_test__iter_rank_cutoffs(self, degree, interspersal):
            predicate = hstrat.StratumRetentionPredicateGeomSeqNthRoot(
                degree=degree,
                interspersal=interspersal,
            )
            rank_cutoffs_by_generation = [
                predicate._iter_rank_cutoffs(g)
                for g in range(10000)
            ]
            zipped = list(zip_equal(*rank_cutoffs_by_generation))
            assert len(zipped) == degree
            for equiv_seq in zipped:
                assert helpers.is_nondecreasing(equiv_seq)

    def _do_test__iter_rank_seps(self, degree, interspersal):
            predicate = hstrat.StratumRetentionPredicateGeomSeqNthRoot(
                degree=degree,
                interspersal=interspersal,
            )
            rank_seps_by_generation = [
                predicate._iter_rank_seps(g)
                for g in range(10000)
            ]
            zipped = list(zip_equal(*rank_seps_by_generation))
            assert len(zipped) == degree
            for equiv_seq in zipped:
                assert helpers.is_nondecreasing(equiv_seq)
                assert all(
                    # is power of 2
                    # https://stackoverflow.com/a/57025941
                    (item & (item-1) == 0) and item
                    for item in equiv_seq
                )

    def _do_test__iter_rank_backstops(self, degree, interspersal):
            predicate = hstrat.StratumRetentionPredicateGeomSeqNthRoot(
                degree=degree,
                interspersal=interspersal,
            )
            rank_backstops_by_generation = [
                predicate._iter_rank_backstops(g)
                for g in range(10000)
            ]
            zipped = list(zip_equal(*rank_backstops_by_generation))
            assert len(zipped) == degree
            for equiv_seq in zipped:
                assert helpers.is_nondecreasing(equiv_seq)

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
                f'def test_CalcRankAtColumnIndex_{degree}_{interspersal}(self): self._do_test_CalcRankAtColumnIndex({degree}, {interspersal})'
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

    def test__iter_target_recencies(self):
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
                self._do_test__iter_target_recencies(degree, interspersal)

    def test__iter_target_ranks(self):
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
                self._do_test__iter_target_ranks(degree, interspersal)

    def test__iter_rank_cutoffs(self):
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
                self._do_test__iter_rank_cutoffs(degree, interspersal)

    def test__iter_rank_seps(self):
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
                self._do_test__iter_rank_seps(degree, interspersal)

    def test__iter_rank_backstops(self):
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
                self._do_test__iter_rank_backstops(degree, interspersal)

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
                predicate = hstrat.StratumRetentionPredicateGeomSeqNthRoot(
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
