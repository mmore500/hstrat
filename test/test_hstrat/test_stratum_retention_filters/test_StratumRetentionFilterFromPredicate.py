from copy import deepcopy
import unittest

from pylib import hstrat


class TestStratumRetentionFilterFromPredicate(unittest.TestCase):

    def test_equality(self):
        assert (
            hstrat.StratumRetentionFilterFromPredicate(
                hstrat.StratumRetentionPredicateStochastic(),
            )
            == hstrat.StratumRetentionFilterFromPredicate(
                hstrat.StratumRetentionPredicateStochastic(),
            )
        )

        original = hstrat.StratumRetentionFilterFromPredicate(
            hstrat.StratumRetentionPredicateMaximal(),
        )
        copy = deepcopy(original)
        assert original == copy


if __name__ == '__main__':
    unittest.main()
