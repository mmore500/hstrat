from copy import deepcopy
import unittest

from hstrat import hstrat


class TestStratumRetentionCondemnerNominalResolution(unittest.TestCase):

    # tests can run independently
    _multiprocess_can_split_ = True

    def test_equality(self):
        assert (
            hstrat.StratumRetentionCondemnerNominalResolution()
            == hstrat.StratumRetentionCondemnerNominalResolution()
        )

        original \
            = hstrat.StratumRetentionCondemnerNominalResolution()
        copy = deepcopy(original)
        assert original == copy

    def test_retention(self):
        control_column = hstrat.HereditaryStratigraphicColumn(
            stratum_ordered_store_factory
                =hstrat.HereditaryStratumOrderedStoreDict,
            stratum_retention_predicate
                =hstrat.StratumRetentionPredicateNominalResolution(),
        )
        test_column = hstrat.HereditaryStratigraphicColumn(
            stratum_ordered_store_factory
                =hstrat.HereditaryStratumOrderedStoreDict,
            stratum_retention_condemner
                =hstrat.StratumRetentionCondemnerNominalResolution(),
        )

        for i in range(1000):
            control_column.DepositStratum()
            test_column.DepositStratum()
            d1, d2 = control_column.DiffRetainedRanks(test_column)
            assert d1 == set() and d2 == set()

    def test_CalcRankAtColumnIndex(self):
        test_condemner = hstrat.StratumRetentionCondemnerNominalResolution()
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
                    index=i,
                    num_strata_deposited=test_column.GetNumStrataDeposited()
                )
                for i in range(test_column.GetNumStrataRetained())
            }
            assert actual_ranks == calcualted_ranks
            # in-progress deposition case
            assert test_condemner.CalcRankAtColumnIndex(
                index=test_column.GetNumStrataRetained(),
                num_strata_deposited=test_column.GetNumStrataDeposited(),
            ) == test_column.GetNumStrataDeposited()

    def test_CalcNumStrataRetainedExact(self):
        test_condemner \
            = hstrat.StratumRetentionCondemnerNominalResolution()
        test_column = hstrat.HereditaryStratigraphicColumn(
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


    def test_CalcNumStrataRetainedUpperBound(self):
        test_condemner \
            = hstrat.StratumRetentionCondemnerNominalResolution()
        test_column = hstrat.HereditaryStratigraphicColumn(
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


if __name__ == '__main__':
    unittest.main()
