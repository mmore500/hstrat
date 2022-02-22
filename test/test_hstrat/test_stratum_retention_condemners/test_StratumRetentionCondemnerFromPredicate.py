from copy import deepcopy
import unittest

from pylib import hstrat


class TestStratumRetentionCondemnerFromPredicate(unittest.TestCase):

    # tests can run independently
    _multiprocess_can_split_ = True

    def test_equality(self):
        assert (
            hstrat.StratumRetentionCondemnerFromPredicate(
                hstrat.StratumRetentionPredicateStochastic(),
            )
            == hstrat.StratumRetentionCondemnerFromPredicate(
                hstrat.StratumRetentionPredicateStochastic(),
            )
        )

        original = hstrat.StratumRetentionCondemnerFromPredicate(
            hstrat.StratumRetentionPredicatePerfectResolution(),
        )
        copy = deepcopy(original)
        assert original == copy

    def test_maximal_retention_condemnation(self):
        maximal_retention_condemner \
            = hstrat.StratumRetentionCondemnerFromPredicate(
                hstrat.StratumRetentionPredicatePerfectResolution(),
        )
        for i in range(100):
            assert list(maximal_retention_condemner(
                retained_ranks=range(i),
                num_stratum_depositions_completed=i,
            )) == []

    def test_minimal_retention_condemnation(self):
        minimal_retention_condemner \
            = hstrat.StratumRetentionCondemnerFromPredicate(
                hstrat.StratumRetentionPredicateNominalResolution(),
        )
        assert list(minimal_retention_condemner(
            retained_ranks=range(0),
            num_stratum_depositions_completed=0,
        )) == []
        assert list(minimal_retention_condemner(
            retained_ranks=range(1),
            num_stratum_depositions_completed=0,
        )) == []
        assert list(minimal_retention_condemner(
            retained_ranks=range(2),
            num_stratum_depositions_completed=1,
        )) == []
        assert list(minimal_retention_condemner(
            retained_ranks=[0,1,2],
            num_stratum_depositions_completed=2,
        )) == [1]
        assert list(minimal_retention_condemner(
            retained_ranks=[0,2,3],
            num_stratum_depositions_completed=3,
        )) == [2]


if __name__ == '__main__':
    unittest.main()
