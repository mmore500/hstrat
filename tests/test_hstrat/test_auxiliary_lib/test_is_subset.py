import numpy as np

from hstrat._auxiliary_lib import is_subset


def test_empty_subset_and_superset():
    subset = np.array([])
    superset = np.array([])
    assert is_subset(subset, superset)


def test_empty_subset_not_empty_superset():
    subset = np.array([])
    superset = np.array([1, 2, 3])
    assert is_subset(subset, superset)


def test_not_empty_subset_empty_superset():
    subset = np.array([1, 2, 3])
    superset = np.array([])
    assert not is_subset(subset, superset)


def test_subset_not_a_subset_of_superset():
    subset = np.array([1, 2, 3, 4])
    superset = np.array([1, 2, 3])
    assert not is_subset(subset, superset)


def test_subset_is_a_subset_of_superset():
    subset = np.array([1, 2, 3])
    superset = np.array([1, 2, 3, 4])
    assert is_subset(subset, superset)
