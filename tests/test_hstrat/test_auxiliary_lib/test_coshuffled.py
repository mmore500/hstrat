from hstrat._auxiliary_lib import coshuffled


def test_coshuffle_conserve_elements():
    a = [1, 2, 3, 4, 5]
    b = [5, 6, 7, 8, 9]
    c = [9, 10, 11, 12, 13]
    a_, b_, c_ = coshuffled(a, b, c)

    assert a != a_
    assert b != b_
    assert c != c_

    assert sorted(a) == sorted(a_)
    assert sorted(b) == sorted(b_)
    assert sorted(c) == sorted(c_)


def test_coshuffle_keep_relative_order():
    a = [1, 2, 3, 4]
    b = [5, 6, 7, 8]
    assert all(y - x == 4 for x, y in zip(*coshuffled(a, b)))


def test_coshuffle_singleton():
    assert ([1], [2], [3]) == coshuffled([1], [2], [3])


def test_coshuffle_empty():
    assert ([], [], []) == coshuffled([], [], [])


def test_coshuffle_singleton2():
    a = [1]
    assert coshuffled(a) == ([1],)


def test_coshuffle_empty2():
    a = []
    assert coshuffled(a) == ([],)


def test_coshuffle_empty3():
    assert coshuffled() == tuple()
