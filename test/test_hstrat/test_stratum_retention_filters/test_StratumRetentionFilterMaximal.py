from copy import deepcopy
import unittest

from pylib import hstrat


class TestStratumRetentionFilterMaximal(unittest.TestCase):

    def test_equality(self):
        assert (
            hstrat.StratumRetentionFilterMaximal()
            == hstrat.StratumRetentionFilterMaximal()
        )

        original = hstrat.StratumRetentionFilterMaximal()
        copy = deepcopy(original)
        assert original == copy


if __name__ == '__main__':
    unittest.main()
