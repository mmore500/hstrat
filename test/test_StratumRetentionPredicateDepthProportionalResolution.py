#!/bin/python3

import unittest

from pylib import HereditaryStratigraphicColumn
from pylib import StratumRetentionPredicateDepthProportionalResolution

class TestStratumRetentionPredicateDepthProportionalResolution(
    unittest.TestCase,
):

    def _do_test_space_complexity(self, min_intervals_divide_into):
        column = HereditaryStratigraphicColumn(
            stratum_retention_predicate
                =StratumRetentionPredicateDepthProportionalResolution(
                    min_intervals_divide_into=min_intervals_divide_into,
                ),
        )

        for generation in range(10000):
            assert column.GetColumnSize() <= min_intervals_divide_into*2 + 1
            column.DepositLayer()


    def test_space_complexity(self):
        for min_intervals_divide_into in [
            1,
            2,
            10,
            42,
            97,
        ]:
            self._do_test_space_complexity(min_intervals_divide_into)


if __name__ == '__main__':
    unittest.main()
