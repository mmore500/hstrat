from copy import deepcopy
import unittest

from pylib import hstrat


class TestStratumRetentionCondemnerMaximal(unittest.TestCase):

    def test_equality(self):
        assert (
            hstrat.StratumRetentionCondemnerMaximal()
            == hstrat.StratumRetentionCondemnerMaximal()
        )

        original = hstrat.StratumRetentionCondemnerMaximal()
        copy = deepcopy(original)
        assert original == copy

    def test_condemnation(self):
        maximal_retention_condemner = hstrat.StratumRetentionCondemnerMaximal()
        for i in range(100):
            assert list(maximal_retention_condemner(
                retained_ranks=range(i),
                num_strata_deposited=i,
            )) == []


if __name__ == '__main__':
    unittest.main()
