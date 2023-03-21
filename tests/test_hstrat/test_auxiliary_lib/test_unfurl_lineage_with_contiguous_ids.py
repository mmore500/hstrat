import numpy as np

from hstrat._auxiliary_lib import unfurl_lineage_with_contiguous_ids


def test_unfurl_lineage():
    ancestor_ids = np.array([3, 2, 2, 3, 3, 1])
    leaf_id = 5
    expected_result = np.array([5, 1, 2])
    result = unfurl_lineage_with_contiguous_ids(ancestor_ids, leaf_id)
    np.testing.assert_array_equal(result, expected_result)


def test_unfurl_lineage_root():
    ancestor_ids = np.array([3, 2, 2, 3, 3, 1])
    leaf_id = 3
    expected_result = np.array([3])
    result = unfurl_lineage_with_contiguous_ids(ancestor_ids, leaf_id)
    np.testing.assert_array_equal(result, expected_result)


def test_unfurl_lineage_singleton():
    ancestor_ids = np.array([0])
    leaf_id = 0
    expected_result = np.array([0])
    result = unfurl_lineage_with_contiguous_ids(ancestor_ids, leaf_id)
    np.testing.assert_array_equal(result, expected_result)
