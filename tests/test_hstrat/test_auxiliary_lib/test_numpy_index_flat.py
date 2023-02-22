import numpy as np

from hstrat._auxiliary_lib import numpy_index_flat


def test_numpy_index_flat_first_occurrence():
    # Test that the function returns the correct index for the first occurrence of an item
    a = np.array([1, 2, 3, 4, 5])
    assert numpy_index_flat(a, 3) == 2
    assert a[numpy_index_flat(a, 3)] == 3
    assert numpy_index_flat(a, 5) == 4
    assert a[numpy_index_flat(a, 5)] == 5
    assert numpy_index_flat(a, 1) == 0
    assert a[numpy_index_flat(a, 1)] == 1

    b = np.array([0, 1, 2, 1, 4])
    assert numpy_index_flat(b, 1) == 1
    assert b[numpy_index_flat(b, 1)] == 1

    c = np.array([1])
    assert numpy_index_flat(c, 1) == 0
    assert c[numpy_index_flat(c, 1)] == 1

    c = np.array([1])
    assert numpy_index_flat(c, 1, search_backwards=True) == 0
    assert c[numpy_index_flat(c, 1, search_backwards=True)] == 1


def test_numpy_index_flat_reverse_index():
    # Test that the function returns the correct index for a reverse indexed array
    a = np.array([5, 4, 3, 2, 1])
    assert numpy_index_flat(a[::-1], 3) == 2


def test_numpy_index_flat_item_not_found():
    # Test that the function returns None when the item is not found in the array
    a = np.array([1, 2, 3, 4, 5])
    assert numpy_index_flat(a, 6) is None

    b = np.array([0, 1, 2, 1, 4])
    assert numpy_index_flat(b, 3) is None

    c = np.array([1])
    assert numpy_index_flat(c, 2) is None


def test_numpy_index_flat_empty_array():
    # Test that the function returns None when the array is empty
    a = np.array([])
    assert numpy_index_flat(a, 1) is None
    assert numpy_index_flat(a, 1, search_backwards=True) is None


def test_numpy_index_flat_reverse():
    # Test that the function returns the correct index for a reverse indexed array
    a = np.array([1, 2, 3, 4, 5])
    assert numpy_index_flat(a, 3, search_backwards=True) == 2
    assert a[numpy_index_flat(a, 3, search_backwards=True)] == 3
    assert numpy_index_flat(a, 6, search_backwards=True) is None
    assert numpy_index_flat(a, 1, search_backwards=True) == 0
    assert a[numpy_index_flat(a, 1, search_backwards=True)] == 1

    b = np.array([0, 1, 2, 1, 4])
    assert numpy_index_flat(b, 1, search_backwards=True) == 3
    assert b[numpy_index_flat(b, 1, search_backwards=True)] == 1
    assert numpy_index_flat(b, 3, search_backwards=True) is None

    c = np.array([1])
    assert numpy_index_flat(c, 1, search_backwards=True) == 0
    assert c[numpy_index_flat(c, 1, search_backwards=True)] == 1
    assert numpy_index_flat(c, 2, search_backwards=True) is None
