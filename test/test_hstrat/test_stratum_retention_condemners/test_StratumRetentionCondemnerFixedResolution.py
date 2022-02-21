from copy import deepcopy
import unittest

from pylib import hstrat


class TestStratumRetentionCondemnerFixedResolution(
    unittest.TestCase,
):

    # tests can run independently
    _multiprocess_can_split_ = True

    def test_equality(self):
        assert (
            hstrat.StratumRetentionCondemnerFixedResolution()
            == hstrat.StratumRetentionCondemnerFixedResolution()
        )

        original = hstrat.StratumRetentionCondemnerFixedResolution()
        copy = deepcopy(original)
        assert original == copy

    def _do_test_retention(
        self,
        fixed_resolution,
    ):
        control_column = hstrat.HereditaryStratigraphicColumn(
            stratum_ordered_store_factory
                =hstrat.HereditaryStratumOrderedStoreDict,
            stratum_retention_predicate
                =hstrat.StratumRetentionPredicateFixedResolution(
                    fixed_resolution=fixed_resolution,
                ),
        )
        test_column = hstrat.HereditaryStratigraphicColumn(
            stratum_ordered_store_factory
                =hstrat.HereditaryStratumOrderedStoreDict,
            stratum_retention_condemner
                =hstrat.StratumRetentionCondemnerFixedResolution(
                    fixed_resolution=fixed_resolution,
                ),
        )

        for i in range(1000):
            control_column.DepositStratum()
            test_column.DepositStratum()
            d1, d2 = control_column.DiffRetainedRanks(test_column)
            assert d1 == set() and d2 == set()

    def test_retention(self):
        for fixed_resolution in [
            1,
            2,
            3,
            7,
            42,
            100,
        ]:
            self._do_test_retention(
                fixed_resolution,
            )


if __name__ == '__main__':
    unittest.main()
