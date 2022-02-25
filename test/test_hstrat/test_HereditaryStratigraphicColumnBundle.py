from copy import deepcopy
import random
import unittest

from pylib import hstrat

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


if __name__ == '__main__':
    unittest.main()
