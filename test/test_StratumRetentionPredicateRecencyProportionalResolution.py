#!/bin/python3

from copy import deepcopy
import unittest
import random

from pylib import HereditaryStratigraphicColumn
from pylib import StratumRetentionPredicateRecencyProportionalResolution

class TestStratumRetentionPredicateDepthProportionalResolution(
    unittest.TestCase,
):

    def _do_test_space_complexity(
        self,
        min_intervals_divide_into,
        num_intervals_recurse_on,
    ):

        predicate = StratumRetentionPredicateRecencyProportionalResolution(
            min_intervals_divide_into=min_intervals_divide_into,
            num_intervals_recurse_on=num_intervals_recurse_on,
        )
        column = HereditaryStratigraphicColumn(
            stratum_retention_predicate=predicate,
        )

        for generation in range(1000):
            assert (
                column.GetColumnSize()
                <= predicate.CalcColumnSizeUpperBound(generation)
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
