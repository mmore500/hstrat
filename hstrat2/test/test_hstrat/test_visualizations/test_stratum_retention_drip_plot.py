import random
import unittest

from hstrat import hstrat

random.seed(1)


class TestStratumRetentionDripPlot(unittest.TestCase):

    # tests can run independently
    _multiprocess_can_split_ = True

    def test(self):
        for predicate in [
            hstrat.StratumRetentionPredicateDepthProportionalResolution(),
            hstrat.StratumRetentionPredicateFixedResolution(),
            hstrat.StratumRetentionPredicateNominalResolution(),
            hstrat.StratumRetentionPredicatePerfectResolution(),
            hstrat.StratumRetentionPredicateRecencyProportionalResolution(),
            hstrat.StratumRetentionPredicateStochastic(),
            hstrat.\
                StratumRetentionPredicateTaperedDepthProportionalResolution(),
        ]:
            hstrat.stratum_retention_drip_plot(predicate, 100, do_show=False)
            hstrat.stratum_retention_drip_plot(predicate, 10, do_show=False)


if __name__ == '__main__':
    unittest.main()
