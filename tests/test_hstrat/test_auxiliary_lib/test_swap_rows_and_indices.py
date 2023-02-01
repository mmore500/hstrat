import unittest

import numpy as np
import pandas as pd

from hstrat._auxiliary_lib import swap_rows_and_indices


class TestOmitLast(unittest.TestCase):

    # tests can run independently
    _multiprocess_can_split_ = True

    def test_default_index(self):

        df = pd.DataFrame(
            np.array([[1, 2], [3, 4], [5, 6]]),
            columns=["a", "b"],
        )

        df_ = df.copy()
        df_ = swap_rows_and_indices(df_, 0, 0)
        assert df_.equals(df)

        df_ = df.copy()
        df_ = swap_rows_and_indices(df_, 0, 1)
        target = pd.DataFrame(
            np.array([[3, 4], [1, 2], [5, 6]]),
            columns=["a", "b"],
            index=[1, 0, 2],
        )

        df_ = swap_rows_and_indices(df_, 1, 0)
        assert df_.equals(df)

        df_ = df.copy()
        df_ = swap_rows_and_indices(df_, 0, 1)
        df_ = swap_rows_and_indices(df_, 1, 2)
        target = pd.DataFrame(
            np.array([[5, 6], [1, 2], [3, 4]]),
            columns=["a", "b"],
            index=[2, 0, 1],
        )

        assert df_.equals(target)

        df_ = df.copy()
        df_ = swap_rows_and_indices(df_, 0, 2)
        target = pd.DataFrame(
            np.array([[5, 6], [3, 4], [1, 2]]),
            columns=["a", "b"],
            index=[2, 1, 0],
        )
        assert df_.equals(target)

    def test_custom_index(self):

        df = pd.DataFrame(
            np.array([[1, 2], [3, 4], [5, 6]]),
            columns=["a", "b"],
            index=["A", "B", "C"],
        )

        df_ = df.copy()
        df_ = swap_rows_and_indices(df_, "A", "A")
        assert df_.equals(df)

        df_ = df.copy()
        df_ = swap_rows_and_indices(df_, "A", "B")
        target = pd.DataFrame(
            np.array([[3, 4], [1, 2], [5, 6]]),
            columns=["a", "b"],
            index=["B", "A", "C"],
        )
        assert df_.equals(target)

        df_ = swap_rows_and_indices(df_, "B", "A")
        assert df_.equals(df)

        df_ = df.copy()
        df_ = swap_rows_and_indices(df_, "A", "B")
        df_ = swap_rows_and_indices(df_, "B", "C")
        target = pd.DataFrame(
            np.array([[5, 6], [1, 2], [3, 4]]),
            columns=["a", "b"],
            index=["C", "A", "B"],
        )
        assert df_.equals(target)

        df_ = df.copy()
        df_ = swap_rows_and_indices(df_, "A", "C")
        target = pd.DataFrame(
            np.array([[5, 6], [3, 4], [1, 2]]),
            columns=["a", "b"],
            index=["C", "B", "A"],
        )
        assert df_.equals(target)


if __name__ == "__main__":
    unittest.main()
