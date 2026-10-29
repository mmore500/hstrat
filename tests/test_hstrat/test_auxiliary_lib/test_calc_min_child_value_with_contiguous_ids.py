import numpy as np

from hstrat._auxiliary_lib import calc_min_child_value_with_contiguous_ids


def test_calc_min_child_value_with_contiguous_ids():
    # 0 <- 1 <- 2
    #       \ <- 3
    #  \ <- 4
    ancestor_ids = np.array([0, 0, 1, 1, 0])
    values = np.array([0.0, 10.0, 30.0, 20.0, 40.0])
    res = calc_min_child_value_with_contiguous_ids(ancestor_ids, values)
    np.testing.assert_array_equal(res, [10.0, 20.0, np.inf, np.inf, np.inf])


def test_calc_min_child_value_with_contiguous_ids_fill_value():
    ancestor_ids = np.array([0, 0])
    values = np.array([0.0, -np.inf])
    res = calc_min_child_value_with_contiguous_ids(
        ancestor_ids, values, fill_value=-1.0
    )
    np.testing.assert_array_equal(res, [-np.inf, -1.0])
