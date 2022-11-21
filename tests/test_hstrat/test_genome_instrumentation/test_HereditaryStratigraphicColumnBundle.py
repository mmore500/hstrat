from copy import deepcopy
import pickle
import tempfile
import unittest

from hstrat import hstrat


class TestHereditaryStratigraphicColumnBundle(unittest.TestCase):

    # tests can run independently
    _multiprocess_can_split_ = True

    def test_equality(self):
        def make_populated_bundle():
            return hstrat.HereditaryStratigraphicColumnBundle(
                {
                    "test": hstrat.HereditaryStratigraphicColumn(),
                    "control": hstrat.HereditaryStratigraphicColumn(
                        stratum_retention_policy=hstrat.perfect_resolution_algo.Policy(),
                    ),
                }
            )

        assert make_populated_bundle() != make_populated_bundle()
        column1 = make_populated_bundle()
        column2 = column1
        assert column1 == column2
        assert column1 == deepcopy(column2)

        column3 = make_populated_bundle()
        assert column3 != column2

    def test_clone(self):
        def make_populated_bundle():
            return hstrat.HereditaryStratigraphicColumnBundle(
                {
                    "test": hstrat.HereditaryStratigraphicColumn(),
                    "control": hstrat.HereditaryStratigraphicColumn(
                        stratum_retention_policy=hstrat.perfect_resolution_algo.Policy(),
                    ),
                }
            )

        column1 = make_populated_bundle()
        column2 = column1.Clone()
        column3 = column1.Clone()

        assert column1 == column2
        assert column2 == column3
        assert column1 == column3

        column1.DepositStratum()

        assert column1 != column2
        assert column2 == column3
        assert column1 != column3

    def test_pickle(self):
        def make_populated_bundle():
            return hstrat.HereditaryStratigraphicColumnBundle(
                {
                    "test": hstrat.HereditaryStratigraphicColumn(),
                    "control": hstrat.HereditaryStratigraphicColumn(
                        stratum_retention_policy=hstrat.perfect_resolution_algo.Policy(),
                    ),
                }
            )

        column1 = make_populated_bundle()
        column2 = column1.Clone()
        column3 = column1.CloneDescendant()

        column3.DepositStratum()

        for __ in range(100):
            column1.DepositStratum()

        for original in column1, column2, column3:
            with tempfile.TemporaryDirectory() as tmp_path:
                with open(f"{tmp_path}/data", "wb") as tmp_file:
                    pickle.dump(original, tmp_file)

                with open(f"{tmp_path}/data", "rb") as tmp_file:
                    reconstituted = pickle.load(tmp_file)
                    assert reconstituted == original

    def test_forwarding_fallback(self):
        bundle1 = hstrat.HereditaryStratigraphicColumnBundle(
            {
                "test": hstrat.HereditaryStratigraphicColumn(
                    stratum_retention_policy=hstrat.nominal_resolution_algo.Policy(),
                    stratum_differentia_bit_width=1,
                ),
                "control": hstrat.HereditaryStratigraphicColumn(
                    stratum_retention_policy=hstrat.perfect_resolution_algo.Policy(),
                ),
            }
        )

        for __ in range(100):
            bundle1.DepositStratum()
        bundle2 = bundle1.Clone()
        for __ in range(100):
            bundle1.DepositStratum()
        for __ in range(100):
            bundle2.DepositStratum()

        assert (
            hstrat.does_have_any_common_ancestor(
                bundle1["test"], bundle2["test"]
            )
            is None
        )
        assert (
            hstrat.does_have_any_common_ancestor(
                bundle1["control"], bundle2["control"]
            )
            is True
        )

        assert (
            hstrat.does_have_any_common_ancestor(
                bundle1["test"], bundle2["test"], confidence_level=0.49
            )
            is True
        )
        assert (
            hstrat.does_have_any_common_ancestor(
                bundle1["control"], bundle2["control"], confidence_level=0.49
            )
            is True
        )

        res = bundle1.GetNumStrataRetained()
        assert (
            0 < res["test"] < res["control"] <= bundle1.GetNumStrataDeposited()
        )

        assert bundle1._stratum_differentia_bit_width == {
            "test": 1,
            "control": 64,
        }


if __name__ == "__main__":
    unittest.main()
