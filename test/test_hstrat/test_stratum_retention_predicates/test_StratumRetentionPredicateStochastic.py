from copy import deepcopy
import unittest

from pylib import hstrat


class TestStratumRetentionPredicateStochastic(unittest.TestCase):

    def test_equality(self):
        assert (
            hstrat.StratumRetentionPredicateStochastic()
            == hstrat.StratumRetentionPredicateStochastic()
        )

        original = hstrat.StratumRetentionPredicateStochastic()
        copy = deepcopy(original)
        assert original == copy


if __name__ == '__main__':
    unittest.main()
