import contexttimer as ctt
import interval_search as inch
import numpy as np

from hstrat._auxiliary_lib import curried_binary_search_jit, jit


def test_curried_binary_search_jit_singleton():
    @jit(nopython=True)
    def predicate(i: int) -> bool:
        return True

    assert curried_binary_search_jit(predicate)(10, 10) == 10


def test_binary_search_jit():
    @jit(nopython=True)
    def predicate(i: int) -> bool:
        return i >= 5

    assert curried_binary_search_jit(predicate)(0, 100) == 5


def test_curried_binary_search_jit_numpy():
    data = np.arange(100)

    @jit(nopython=True)
    def predicate(i: int) -> bool:
        return data[i] > data[::-1][i]

    assert curried_binary_search_jit(predicate)(0, 100) == inch.binary_search(
        predicate, 0, 100
    )


def test_fruitless_curried_binary_search_jit():
    @jit(nopython=True)
    def predicate_false(i: int) -> bool:
        return False

    assert curried_binary_search_jit(predicate_false)(0, 100) is None


def test_empty_curried_binary_search_jit():
    @jit(nopython=True)
    def predicate_false(i: int) -> bool:
        return False

    @jit(nopython=True)
    def predicate_true(i: int) -> bool:
        return False

    assert curried_binary_search_jit(predicate_false)(100, 99) is None
    assert curried_binary_search_jit(predicate_false)(100, 0) is None
    assert curried_binary_search_jit(predicate_true)(100, 99) is None
    assert curried_binary_search_jit(predicate_true)(100, 0) is None


def test_benchmark():
    @jit(nopython=True)
    def predicate(i: int) -> bool:
        return i <= 5

    do_search = curried_binary_search_jit(predicate)
    do_search(0, 2**31)

    with ctt.Timer(factor=1000) as t_jit:
        for __ in range(10000):
            do_search(0, 2**31)

    with ctt.Timer(factor=1000) as t_vanilla:
        for __ in range(10000):
            inch.binary_search(lambda x: x <= 5, 0, 2**31)

    with ctt.Timer(factor=1000) as t_vanilla_jitpred:
        for __ in range(10000):
            inch.binary_search(predicate, 0, 2**31)

    print(f"t_jit={t_jit}")
    print(f"t_vanilla={t_vanilla}")
    print(f"t_vanilla_jitpred={t_vanilla_jitpred}")
