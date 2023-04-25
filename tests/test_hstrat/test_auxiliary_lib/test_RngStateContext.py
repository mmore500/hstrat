import random
import typing

import pytest

from hstrat._auxiliary_lib import RngStateContext


@pytest.fixture
def seed_values() -> typing.Dict[int, typing.List[float]]:
    """Returns a dictionary of seed values to their first five elements.

    Returns:
    --------
    seed_values: Dict[int, List[float]]
        A dictionary mapping seed values to a list of their first five elements.
    """
    seed_list = [10, 20, 30, 42, 50, 420, 12345]
    num_elements = 5
    seed_values = {}
    for seed in seed_list:
        random.seed(seed)
        seed_values[seed] = [random.random() for _ in range(num_elements)]
    return seed_values


def test_reseeded_rng_temporarily_reseed_rng(seed_values):
    outer_seed = 42
    inner_seed = 420

    random.seed(outer_seed)
    assert random.random() == seed_values[outer_seed][0]
    with RngStateContext(inner_seed):
        for i, __ in enumerate(seed_values[inner_seed]):
            assert random.random() == seed_values[inner_seed][i]
    assert random.random() == seed_values[outer_seed][1]


def test_reseeded_rng_temporarily_reseed_rng_multiple_times(seed_values):
    seed1 = 10
    expected_values1 = seed_values[seed1]
    with RngStateContext(seed1):
        for i, __ in enumerate(expected_values1):
            assert random.random() == expected_values1[i]

    seed2 = 20
    expected_values2 = seed_values[seed2]
    with RngStateContext(seed2):
        for i, __ in enumerate(expected_values2):
            assert random.random() == expected_values2[i]

    seed3 = 30
    expected_values3 = seed_values[seed3]
    with RngStateContext(seed3):
        for i, __ in enumerate(expected_values3):
            assert random.random() == expected_values3[i]

    assert random.random() != expected_values3[-1]
    assert random.random() != expected_values2[-1]
    assert random.random() != expected_values1[-1]


def test_reseeded_rng_nested_reseeding(seed_values):
    outer_seed = 42
    inner_seed = 420

    random.seed(outer_seed)
    assert random.random() == seed_values[outer_seed][0]

    with RngStateContext(inner_seed):
        assert random.random() == seed_values[inner_seed][0]

        inner_inner_seed = 12345
        with RngStateContext(inner_inner_seed):
            for j, __ in enumerate(seed_values[inner_inner_seed]):
                assert random.random() == seed_values[inner_inner_seed][j]

        assert random.random() == seed_values[inner_seed][1]

    assert random.random() == seed_values[outer_seed][1]


def test_reseeded_rng_exception(seed_values):
    seed = 50
    expected_value = seed_values[seed][0]
    with pytest.raises(ValueError):
        with RngStateContext(seed):
            assert random.random() == expected_value
            raise ValueError()
    assert random.random() != expected_value
