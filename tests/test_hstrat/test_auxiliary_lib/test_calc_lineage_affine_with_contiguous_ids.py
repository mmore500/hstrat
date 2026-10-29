import numpy as np

from hstrat._auxiliary_lib import calc_lineage_affine_with_contiguous_ids


def test_calc_lineage_affine_with_contiguous_ids():
    # 0 <- 1 <- 2
    #  \ <- 3
    # 4
    ancestor_ids = np.array([0, 0, 1, 0, 4])
    multipliers = np.array([9.0, 2.0, 3.0, 0.5, 9.0])
    addends = np.array([1.0, 1.0, 1.0, 2.0, 5.0])
    res = calc_lineage_affine_with_contiguous_ids(
        ancestor_ids, multipliers, addends
    )
    np.testing.assert_allclose(res, [1.0, 3.0, 10.0, 2.5, 5.0])


def test_calc_lineage_affine_with_contiguous_ids_empty():
    res = calc_lineage_affine_with_contiguous_ids(
        np.array([], dtype=int), np.array([]), np.array([])
    )
    assert len(res) == 0
