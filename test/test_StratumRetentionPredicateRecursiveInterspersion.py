#!/bin/python3

from copy import deepcopy
import itertools as it
import unittest
import random

random.seed(1)

from pylib import HereditaryStratigraphicColumn
from pylib import StratumRetentionPredicateRecursiveInterspersion


class TestStratumRetentionPredicateRecursiveInterspersion(
    unittest.TestCase,
):

    def test_equality(self):
        assert (
            StratumRetentionPredicateRecursiveInterspersion()
            == StratumRetentionPredicateRecursiveInterspersion()
        )

        original1 = StratumRetentionPredicateRecursiveInterspersion(
            min_intervals_divide_into=10,
            num_intervals_recurse_on=5,
        )
        original2 = StratumRetentionPredicateRecursiveInterspersion(
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
        predicate = StratumRetentionPredicateRecursiveInterspersion(
            min_intervals_divide_into=min_intervals_divide_into,
            num_intervals_recurse_on=num_intervals_recurse_on,
        )
        column = HereditaryStratigraphicColumn(
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
            (10,1),
            (10,5),
            #(10,9), TODO
            (42, 1),
            (42, 21),
        ]:
            self._do_test_space_complexity(
                min_intervals_divide_into,
                num_intervals_recurse_on,
            )


if __name__ == '__main__':
    unittest.main()
