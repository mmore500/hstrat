import unittest

from hstrat2 import hstrat


class TestStratumRetentionDripPlot(unittest.TestCase):

    # tests can run independently
    _multiprocess_can_split_ = True

    def test(self):
        for policy in [
            hstrat.fixed_resolution_policy.Policy(10),
            hstrat.nominal_resolution_policy.Policy(),
            hstrat.perfect_resolution_policy.Policy(),
        ]:
            hstrat.stratum_retention_drip_plot(policy, 100, do_show=False)
            hstrat.stratum_retention_drip_plot(policy, 10, do_show=False)


if __name__ == '__main__':
    unittest.main()
