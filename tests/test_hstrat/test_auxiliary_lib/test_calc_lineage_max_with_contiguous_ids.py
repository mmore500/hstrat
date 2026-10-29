import numpy as np

from hstrat._auxiliary_lib import calc_lineage_max_with_contiguous_ids


def test_calc_lineage_max_with_contiguous_ids():
    # 0 <- 1 <- 2 <- 3
    #  \ <- 4
    ancestor_ids = np.array([0, 0, 1, 2, 0])
    values = np.array([1.0, 5.0, 2.0, 7.0, 0.0])
    res = calc_lineage_max_with_contiguous_ids(ancestor_ids, values)
    np.testing.assert_array_equal(res, [1.0, 5.0, 5.0, 7.0, 1.0])
    np.testing.assert_array_equal(values, [1.0, 5.0, 2.0, 7.0, 0.0])


def test_calc_lineage_max_with_contiguous_ids_nan():
    # 0 <- 1 <- 2 <- 3
    ancestor_ids = np.array([0, 0, 1, 2])
    values = np.array([np.nan, 5.0, np.nan, 2.0])
    res = calc_lineage_max_with_contiguous_ids(ancestor_ids, values)
    np.testing.assert_array_equal(res, [np.nan, 5.0, np.nan, 5.0])
