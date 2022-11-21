from copy import deepcopy
import pickle
import tempfile
import unittest

from hstrat import hstrat


class TestHereditaryStratum(unittest.TestCase):

    # tests can run independently
    _multiprocess_can_split_ = True

    def test_deposition_rank(self):
        assert (
            hstrat.HereditaryStratum(
                deposition_rank=42,
            ).GetDepositionRank()
            == 42
        )

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
        def stratum_factory():
            return hstrat.HereditaryStratum(deposition_rank=42)

        assert stratum_factory() != stratum_factory()
        stratum1 = stratum_factory()
        stratum2 = stratum1
        assert stratum1 == stratum2
        assert stratum1 == deepcopy(stratum2)

    def test_pickle(self):
        original = hstrat.HereditaryStratum()
        with tempfile.TemporaryDirectory() as tmp_path:
            with open(f"{tmp_path}/data", "wb") as tmp_file:
                pickle.dump(original, tmp_file)

            with open(f"{tmp_path}/data", "rb") as tmp_file:
                reconstituted = pickle.load(tmp_file)
                assert reconstituted == original
                assert reconstituted != hstrat.HereditaryStratum()


if __name__ == "__main__":
    unittest.main()
