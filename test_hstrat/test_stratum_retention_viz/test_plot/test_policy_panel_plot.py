import unittest

from hstrat import hstrat


class TestPolicyPanelPlot(unittest.TestCase):

    # tests can run independently
    _multiprocess_can_split_ = True

    def test(self):
        for policy in [
            hstrat.fixed_resolution_algo.Policy(10),
            hstrat.nominal_resolution_algo.Policy(),
            hstrat.perfect_resolution_algo.Policy(),
        ]:
            hstrat.policy_panel_plot(policy, 100, do_show=False)
            hstrat.policy_panel_plot(policy, 10, do_show=False)


if __name__ == "__main__":
    unittest.main()
