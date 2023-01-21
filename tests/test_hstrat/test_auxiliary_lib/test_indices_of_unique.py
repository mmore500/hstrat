import unittest

import contexttimer as ctt
import numpy as np
import pandas as pd

from hstrat._auxiliary_lib import indices_of_unique


class TestIndicesOfUnique(unittest.TestCase):

    # tests can run independently
    _multiprocess_can_split_ = True

    def test_empty(self):
        assert len(indices_of_unique(np.array([]))) == 0

    def test_singleton(self):
        assert all(indices_of_unique(np.array([-1])) == np.array([0]))
        assert all(indices_of_unique(np.array([0])) == np.array([0]))
        assert all(indices_of_unique(np.array([1])) == np.array([0]))

    def test_pair(self):
        assert all(indices_of_unique(np.array([-1, 1])) == np.array([0, 1]))
        assert all(indices_of_unique(np.array([-1, -1])) == np.array([0]))
        assert all(indices_of_unique(np.array([0, 0])) == np.array([0]))
        assert all(indices_of_unique(np.array([0, 1])) == np.array([0, 1]))

    def test_triple(self):
        assert all(
            indices_of_unique(np.array([0, -1, 1])) == np.array([0, 1, 2])
        )
        assert all(
            indices_of_unique(np.array([-1, 1, -1])) == np.array([0, 1])
        )
        assert all(indices_of_unique(np.array([1, 0, 0])) == np.array([0, 1]))
        assert all(indices_of_unique(np.array([0, 0, 1])) == np.array([0, 2]))
        assert all(indices_of_unique(np.array([0, 0, 0])) == np.array([0]))

    def test_benchmark(self):
        d1 = np.arange(1000000)
        np.random.shuffle(d1)
        d2 = np.repeat(np.arange(1000), 1000)
        np.random.shuffle(d2)
        d3 = np.repeat(np.arange(1000), 1000)

        with ctt.Timer(factor=1000) as t1_hstrat:
            indices_of_unique(d1)

        with ctt.Timer(factor=1000) as t2_hstrat:
            indices_of_unique(d2)

        with ctt.Timer(factor=1000) as t3_hstrat:
            indices_of_unique(d3)

        with ctt.Timer(factor=1000) as t1_numpy:
            np.unique(d1, return_index=True)

        with ctt.Timer(factor=1000) as t2_numpy:
            np.unique(d2, return_index=True)

        with ctt.Timer(factor=1000) as t3_numpy:
            np.unique(d3, return_index=True)

        with ctt.Timer(factor=1000) as t1_pandas:
            pd.unique(d1)

        with ctt.Timer(factor=1000) as t2_pandas:
            pd.unique(d2)

        with ctt.Timer(factor=1000) as t3_pandas:
            pd.unique(d3)

        print()
        print(
            f"t1_hstrat.elapsed={t1_hstrat.elapsed} "
            f"t2_hstrat.elapsed={t2_hstrat.elapsed} "
            f"t3_hstrat.elapsed={t3_hstrat.elapsed} "
        )
        print(
            f"t1_numpy.elapsed={t1_numpy.elapsed} "
            f"t2_numpy.elapsed={t2_numpy.elapsed} "
            f"t3_numpy.elapsed={t3_numpy.elapsed} "
        )
        print(
            f"t1_pandas.elapsed={t1_pandas.elapsed} "
            f"t2_pandas.elapsed={t2_pandas.elapsed} "
            f"t3_pandas.elapsed={t3_pandas.elapsed} "
        )


if __name__ == "__main__":
    unittest.main()
