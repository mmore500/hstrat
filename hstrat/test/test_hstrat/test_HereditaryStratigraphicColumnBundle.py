from copy import deepcopy
import random
import unittest

from hstrat import hstrat

random.seed(1)


class TestHereditaryStratum(unittest.TestCase):

    # tests can run independently
    _multiprocess_can_split_ = True

    def test_equality(self):
        def make_populated_bundle():
            return hstrat.HereditaryStratigraphicColumnBundle({
                'test' : hstrat.HereditaryStratigraphicColumn(
                ),
                'control' : hstrat.HereditaryStratigraphicColumn(
                    stratum_retention_condemner
                        =hstrat.StratumRetentionCondemnerPerfectResolution(),
                ),
            })

        assert make_populated_bundle() != make_populated_bundle()
        column1 = make_populated_bundle()
        column2 = column1
        assert column1 == column2
        assert column1 == deepcopy(column2)

        column3 = make_populated_bundle()
        assert column3 != column2

    def test_clone(self):
        def make_populated_bundle():
            return hstrat.HereditaryStratigraphicColumnBundle({
                'test' : hstrat.HereditaryStratigraphicColumn(
                ),
                'control' : hstrat.HereditaryStratigraphicColumn(
                    stratum_retention_condemner
                        =hstrat.StratumRetentionCondemnerPerfectResolution(),
                ),
            })

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

    def test_forwarding_fallback(self):
        bundle1 = hstrat.HereditaryStratigraphicColumnBundle({
            'test' : hstrat.HereditaryStratigraphicColumn(
                stratum_retention_condemner
                    =hstrat.StratumRetentionCondemnerNominalResolution(),
                stratum_differentia_bit_width=1,
            ),
            'control' : hstrat.HereditaryStratigraphicColumn(
                stratum_retention_condemner
                    =hstrat.StratumRetentionCondemnerPerfectResolution(),
            ),
        })

        for __ in range(100): bundle1.DepositStratum()
        bundle2 = bundle1.Clone()
        for __ in range(100): bundle1.DepositStratum()
        for __ in range(100): bundle2.DepositStratum()

        res = bundle1.HasAnyCommonAncestorWith(bundle2)
        assert res['test'] is None
        assert res['control'] == True

        res = bundle1.HasAnyCommonAncestorWith(bundle2, confidence_level=0.49)
        assert res['test'] == True
        assert res['control'] == True

        res = bundle1.GetNumStrataRetained()
        assert \
            0 < res['test'] < res['control'] <= bundle1.GetNumStrataDeposited()

        assert bundle1._stratum_differentia_bit_width == {
            'test' : 1,
            'control' : 64,
        }

if __name__ == '__main__':
    unittest.main()
