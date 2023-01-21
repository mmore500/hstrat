import itertools as it

import numpy as np
import pytest

from hstrat._auxiliary_lib import apply_swaps


@pytest.mark.parametrize(
    "pop_size",
    [
        0,
        1,
        2,
        5,
        100,
    ],
)
def test_apply_zero_swaps(pop_size):

    iota = np.arange(pop_size)
    apply_swaps(iota, np.array([], dtype=int), np.array([], dtype=int))
    assert len(set(iota)) == len(iota)
    assert all(iota == np.arange(pop_size))


@pytest.mark.parametrize(
    "pop_size",
    [
        1,
        2,
        5,
        100,
    ],
)
def test_apply_one_swap(pop_size):

    for operand in [np.array([0]), np.array([-1])]:
        iota = np.arange(pop_size)
        apply_swaps(iota, operand, operand)
        assert all(iota == np.arange(pop_size))

    for operands in it.permutations([np.array([0]), np.array([-1])]):
        iota = np.arange(pop_size)
        apply_swaps(iota, *operands)
        assert len(set(iota)) == len(iota)
        assert iota[0] == pop_size - 1
        assert iota[-1] == 0

    target_idx = min(pop_size - 1, 3)
    for operands in it.permutations(
        [np.array([target_idx]), np.array([target_idx - 1])]
    ):
        iota = np.arange(pop_size)

        apply_swaps(iota, *operands)
        assert len(set(iota)) == len(iota)
        assert iota[target_idx] == max(target_idx - 1, 0)
        assert iota[target_idx - 1] == target_idx


@pytest.mark.parametrize(
    "pop_size",
    [
        3,
        5,
        100,
    ],
)
def test_apply_two_swaps(pop_size):

    iota = np.arange(pop_size)
    apply_swaps(iota, np.array([0, 1]), np.array([1, 2]))
    assert iota[0] == 1
    assert iota[1] == 2
    assert iota[2] == 0

    if pop_size > 3:
        iota = np.arange(pop_size)
        apply_swaps(iota, np.array([0, -1]), np.array([1, -2]))
        assert iota[0] == 1
        assert iota[1] == 0
        assert iota[-1] == pop_size - 2
        assert iota[-2] == pop_size - 1


@pytest.mark.parametrize(
    "pop_size",
    [
        1,
        2,
        5,
        100,
    ],
)
@pytest.mark.parametrize(
    "num_swaps",
    [
        0,
        1,
        2,
        5,
        100,
        1000,
    ],
)
def test_apply_swaps_conserves(pop_size, num_swaps):
    iota = np.arange(pop_size)
    swap_from_idxs = np.random.randint(pop_size, size=num_swaps)
    swap_to_idxs = np.random.randint(pop_size, size=num_swaps)
    apply_swaps(iota, swap_from_idxs, swap_to_idxs)
    assert len(set(iota)) == len(iota)


@pytest.mark.parametrize(
    "pop_size",
    [
        1,
        2,
        5,
        100,
    ],
)
@pytest.mark.parametrize(
    "num_swaps",
    [
        0,
        1,
        2,
        5,
        100,
        1000,
    ],
)
def test_apply_swaps_decomposes(pop_size, num_swaps):
    for split in range(pop_size):
        iota = np.arange(pop_size)
        swap_from_idxs = np.random.randint(pop_size, size=num_swaps)
        swap_to_idxs = np.random.randint(pop_size, size=num_swaps)
        apply_swaps(iota, swap_from_idxs[:split], swap_to_idxs[:split])
        apply_swaps(iota, swap_from_idxs[split:], swap_to_idxs[split:])

        iota2 = np.arange(pop_size)
        apply_swaps(iota2, swap_from_idxs, swap_to_idxs)

        assert all(iota == iota2)


@pytest.mark.parametrize(
    "pop_size",
    [
        1,
        2,
        5,
        100,
    ],
)
@pytest.mark.parametrize(
    "num_swaps",
    [
        0,
        1,
        2,
        5,
        100,
        1000,
    ],
)
def test_apply_swaps_reversible(pop_size, num_swaps):
    iota = np.arange(pop_size)
    swap_from_idxs = np.random.randint(pop_size, size=num_swaps)
    swap_to_idxs = np.random.randint(pop_size, size=num_swaps)
    apply_swaps(iota, swap_from_idxs, swap_to_idxs)
    apply_swaps(iota, swap_from_idxs[::-1], swap_to_idxs[::-1])
    assert all(iota == np.arange(pop_size))
