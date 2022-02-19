from copy import deepcopy
import itertools as it
import random
import unittest

random.seed(1)

from pylib import hstrat


class TestStratumRetentionPredicateRecursiveInterspersion(
    unittest.TestCase,
):

    def test_equality(self):
        assert (
            hstrat.StratumRetentionPredicateRecursiveInterspersion()
            == hstrat.StratumRetentionPredicateRecursiveInterspersion()
        )

        original1 = hstrat.StratumRetentionPredicateRecursiveInterspersion(
            min_intervals_divide_into=10,
            num_intervals_recurse_on=5,
        )
        original2 = hstrat.StratumRetentionPredicateRecursiveInterspersion(
            min_intervals_divide_into=10,
            num_intervals_recurse_on=4,
        )
        copy1 = deepcopy(original1)
        assert original1 == copy1
        assert original1 != original2
        assert copy1 != original2

    def _do_test_space_complexity(
        self,
        min_intervals_divide_into,
        num_intervals_recurse_on,
    ):
        predicate = hstrat.StratumRetentionPredicateRecursiveInterspersion(
            min_intervals_divide_into=min_intervals_divide_into,
            num_intervals_recurse_on=num_intervals_recurse_on,
        )
        column = hstrat.HereditaryStratigraphicColumn(
            stratum_retention_predicate=predicate,
        )

        for generation in range(1000):
            assert (
                column.GetNumStrataRetained()
                <= predicate.CalcNumStrataRetainedUpperBound(generation)
            )

    def test_space_complexity(self):
        for min_intervals_divide_into, num_intervals_recurse_on in [
            (2,1),
            (3,1),
            (10,1),
            (10,5),
            (10,9),
            (42, 1),
            (42, 21),
            (100, 50),
            (202, 101),
        ]:
            self._do_test_space_complexity(
                min_intervals_divide_into,
                num_intervals_recurse_on,
            )

    def _do_test_deep_space_complexity(
        self,
        min_intervals_divide_into,
        num_intervals_recurse_on,
    ):
        test_predicate = hstrat.StratumRetentionPredicateRecursiveInterspersion(
            min_intervals_divide_into=min_intervals_divide_into,
            num_intervals_recurse_on=num_intervals_recurse_on,
        )
        individual = hstrat.HereditaryStratigraphicColumn(
            stratum_retention_predicate=test_predicate,
        )

        snapshots = [individual]
        for snapshot in range(100):
                for fastforward in range(100):
                        individual.DepositStratum()
                snapshots.append(individual.Clone())


        for snapshot in snapshots:
            target_space = test_predicate.CalcNumStrataRetainedUpperBound(
                num_strata_deposited=snapshot.GetNumStrataDeposited(),
            )
            assert snapshot.GetNumStrataRetained() <= target_space, (
                min_intervals_divide_into,
                num_intervals_recurse_on,
                snapshot.GetNumStrataRetained(),
                target_space,
                snapshot.GetNumStrataDeposited(),
            )

    def test_deep_space_complexity(self):
        for min_intervals_divide_into, num_intervals_recurse_on in [
            (2,1),
            (3,1),
            (10,1),
            (10,5),
            (10,9),
            (42, 1),
            (42, 21),
            (100, 50),
            (202, 101),
        ]:
            self._do_test_deep_space_complexity(
                min_intervals_divide_into,
                num_intervals_recurse_on,
            )

if __name__ == '__main__':
    unittest.main()
