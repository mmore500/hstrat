from copy import deepcopy
import random
import unittest

from pylib import hstrat

random.seed(1)


class TestHereditaryStratum(unittest.TestCase):

    # tests can run independently
    _multiprocess_can_split_ = True

    def test_deposition_rank(self):
        assert hstrat.HereditaryStratum(
            deposition_rank=42,
        ).GetDepositionRank() == 42

    def test_differentia_generation(self):
        original1 = hstrat.HereditaryStratum(
            deposition_rank=42,
        )
        copy1 = deepcopy(original1)
        original2 = hstrat.HereditaryStratum(
            deposition_rank=42,
        )

        assert original1 == copy1
        assert original1 != original2
        assert copy1 != original2

        assert original1.GetDifferentia() == copy1.GetDifferentia()
        assert original1.GetDifferentia() != original2.GetDifferentia()
        assert copy1.GetDifferentia() != original2.GetDifferentia()

    def test_equality1(self):
        assert hstrat.HereditaryStratum() != hstrat.HereditaryStratum()
        stratum1 = hstrat.HereditaryStratum()
        stratum2 = stratum1
        assert stratum1 == stratum2
        assert stratum1 == deepcopy(stratum2)

    def test_equality2(self):
        stratum_factory = lambda: hstrat.HereditaryStratum(deposition_rank=42)
        assert stratum_factory() != stratum_factory()
        stratum1 = stratum_factory()
        stratum2 = stratum1
        assert stratum1 == stratum2
        assert stratum1 == deepcopy(stratum2)


if __name__ == '__main__':
    unittest.main()
