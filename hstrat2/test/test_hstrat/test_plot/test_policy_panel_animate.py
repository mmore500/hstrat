import unittest

from hstrat2 import hstrat


class TestPolicyPanelAnimate(unittest.TestCase):

    # tests can run independently
    _multiprocess_can_split_ = True

    def test(self):
        for policy in [
            hstrat.nominal_resolution_policy.Policy(),
            hstrat.perfect_resolution_policy.Policy(),
            hstrat.recency_proportional_resolution_policy.Policy(4),
        ]:
            hstrat.policy_panel_animate(policy, 100, do_show=False)
            hstrat.policy_panel_animate(policy, 10, do_show=False)


if __name__ == '__main__':
    unittest.main()
