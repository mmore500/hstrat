import numpy as np

from hstrat._auxiliary_lib import jit, reversed_enumerate


def test_reversed_enumerate_list():
    lst = [1, 2, 3, 4]
    assert list(reversed_enumerate(lst)) == [(3, 4), (2, 3), (1, 2), (0, 1)]


def test_reversed_enumerate_str():
    s = "hello"
    assert list(reversed_enumerate(s)) == [
        (4, "o"),
        (3, "l"),
        (2, "l"),
        (1, "e"),
        (0, "h"),
    ]


def test_reversed_enumerate_empty():
    e = []
    assert list(reversed_enumerate(e)) == []


def test_reversed_enumerate_single_element():
    e = [1]
    assert list(reversed_enumerate(e)) == [(0, 1)]


def test_reversed_enumerate_tuple():
    t = (1, 2, 3)
    assert list(reversed_enumerate(t)) == [(2, 3), (1, 2), (0, 1)]


def test_reversed_enumerate_is_reverse():
    lst = [1, 2, 3, 4]
    assert [*reversed_enumerate(lst)] == [*reversed([*enumerate(lst)])]


def test_reversed_enumerate_is_jitable():
    reversed_enumerate_jit = jit(nopython=True)(reversed_enumerate)
    a = np.array([1, 2, 3, 4])
    assert list(reversed_enumerate_jit(a)) == [(3, 4), (2, 3), (1, 2), (0, 1)]
