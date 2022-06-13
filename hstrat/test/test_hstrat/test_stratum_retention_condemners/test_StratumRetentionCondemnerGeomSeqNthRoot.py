from copy import deepcopy
import unittest

from hstrat import hstrat


class TestStratumRetentionCondemnerGeomSeqNthRoot(
    unittest.TestCase,
):

    # tests can run independently
    _multiprocess_can_split_ = True

    def test_equality(self):
        assert (
            hstrat.StratumRetentionCondemnerGeomSeqNthRoot()
            ==
            hstrat.StratumRetentionCondemnerGeomSeqNthRoot()
        )

        original \
          = hstrat.StratumRetentionCondemnerGeomSeqNthRoot()
        copy = deepcopy(original)
        assert original == copy

    def _do_test_retention(
        self,
        degree,
        interspersal,
    ):
        control_column = hstrat.HereditaryStratigraphicColumn(
            stratum_ordered_store_factory
                =hstrat.HereditaryStratumOrderedStoreDict,
            stratum_retention_predicate
            =hstrat.StratumRetentionPredicateGeomSeqNthRoot(
                    degree=degree,
                    interspersal=interspersal,
                ),
        )
        test_column = hstrat.HereditaryStratigraphicColumn(
            stratum_ordered_store_factory
                =hstrat.HereditaryStratumOrderedStoreDict,
            stratum_retention_condemner
            =hstrat.StratumRetentionCondemnerGeomSeqNthRoot(
                    degree=degree,
                    interspersal=interspersal,
                ),
        )

        for i in range(1000):
            control_column.DepositStratum()
            test_column.DepositStratum()
            d1, d2 = control_column.DiffRetainedRanks(test_column)
            assert d1 == set() and d2 == set()

    def test_retention(self):
        for degree in [
            1,
            2,
            3,
            9,
            10,
            101,
        ]:
            for interspersal in [
                1,
                2,
                5,
            ]:
                self._do_test_retention(
                    degree,
                    interspersal,
                )

    def _do_test_CalcRankAtColumnIndex(
        self,
        degree,
        interspersal,
    ):
        test_condemner \
           = hstrat.StratumRetentionCondemnerGeomSeqNthRoot(
                degree=degree,
                interspersal=interspersal,
            )
        test_column = hstrat.HereditaryStratigraphicColumn(
            always_store_rank_in_stratum=True,
            stratum_ordered_store_factory
                =hstrat.HereditaryStratumOrderedStoreDict,
            stratum_retention_condemner=test_condemner,
        )

        for i in range(10000):
            test_column.DepositStratum()
            actual_ranks = { *test_column.GetRetainedRanks() }
            calcualted_ranks = {
                test_condemner.CalcRankAtColumnIndex(
                    index=j,
                    num_strata_deposited=test_column.GetNumStrataDeposited(),
                )
                for j in range(test_column.GetNumStrataRetained())
            }
            assert actual_ranks == calcualted_ranks
            # in-progress deposition case
            assert test_condemner.CalcRankAtColumnIndex(
                index=test_column.GetNumStrataRetained(),
                num_strata_deposited=test_column.GetNumStrataDeposited(),
            ) == test_column.GetNumStrataDeposited()

    def test_CalcRankAtColumnIndex(self):
        for degree in [
            1,
            2,
            3,
            9,
            10,
            101,
        ]:
            for interspersal in [
                1,
                2,
                5,
            ]:
                self._do_test_CalcRankAtColumnIndex(
                    degree,
                    interspersal,
                )

    def _do_test_CalcNumStrataRetainedExact(
        self,
        degree,
        interspersal,
    ):
        test_condemner \
           = hstrat.StratumRetentionCondemnerGeomSeqNthRoot(
                degree=degree,
                interspersal=interspersal,
            )
        test_column = hstrat.HereditaryStratigraphicColumn(
            always_store_rank_in_stratum=True,
            stratum_ordered_store_factory
                =hstrat.HereditaryStratumOrderedStoreDict,
            stratum_retention_condemner=test_condemner,
        )

        assert 0 == test_condemner.CalcNumStrataRetainedExact(
            num_strata_deposited=0,
        )
        for i in range(10000):
            calculated_num_retained = test_condemner.CalcNumStrataRetainedExact(
                num_strata_deposited=test_column.GetNumStrataDeposited(),
            )
            observed_num_retained = test_column.GetNumStrataRetained()
            assert calculated_num_retained == observed_num_retained
            test_column.DepositStratum()

    def test_CalcNumStrataRetainedExact(self):
        for degree in [
            1,
            2,
            3,
            9,
            10,
            101,
        ]:
            for interspersal in [
                1,
                2,
                5,
            ]:
                self._do_test_CalcNumStrataRetainedExact(
                    degree,
                    interspersal,
                )


    def _do_test_CalcNumStrataRetainedUpperBound(
        self,
        degree,
        interspersal,
    ):
        test_condemner \
           = hstrat.StratumRetentionCondemnerGeomSeqNthRoot(
                degree=degree,
                interspersal=interspersal,
            )
        test_column = hstrat.HereditaryStratigraphicColumn(
            always_store_rank_in_stratum=True,
            stratum_ordered_store_factory
                =hstrat.HereditaryStratumOrderedStoreDict,
            stratum_retention_condemner=test_condemner,
        )

        assert 0 <= test_condemner.CalcNumStrataRetainedUpperBound(
            num_strata_deposited=0,
        )
        for i in range(10000):
            calculated_num_retained_bound \
                = test_condemner.CalcNumStrataRetainedUpperBound(
                    num_strata_deposited=test_column.GetNumStrataDeposited(),
            )
            observed_num_retained = test_column.GetNumStrataRetained()
            assert calculated_num_retained_bound >= observed_num_retained
            test_column.DepositStratum()

    def test_CalcNumStrataRetainedUpperBound(self):
        for degree in [
            1,
            2,
            3,
            9,
            10,
            101,
        ]:
            for interspersal in [
                1,
                2,
                5,
            ]:
                self._do_test_CalcNumStrataRetainedUpperBound(
                    degree,
                    interspersal,
                )


if __name__ == '__main__':
    unittest.main()
