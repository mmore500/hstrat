import random
import typing

import numpy as np
import pytest

from hstrat._auxiliary_lib import RngStateContext
from hstrat._auxiliary_lib._jit import jit


@jit(nopython=True)
def _generate_jitted_random_values(n: int) -> np.ndarray:
    """Generate random values from within a jitted context."""
    result = np.empty(n)
    for i in range(n):
        result[i] = np.random.random()
    return result


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


def test_rng_state_context_jitted_deterministic():
    """Regression test: RngStateContext must seed numba's internal PRNG so
    that jitted code within the context produces deterministic values."""
    n = 10
    results = []
    for _rep in range(3):
        with RngStateContext(42):
            results.append(_generate_jitted_random_values(n))

    for a, b in zip(results, results[1:]):
        np.testing.assert_array_equal(a, b)


def test_rng_state_context_jitted_different_seeds():
    """Regression test: different seeds in RngStateContext produce different
    jitted random values."""
    n = 10
    results = []
    for seed in range(3):
        with RngStateContext(seed):
            results.append(_generate_jitted_random_values(n))

    for a, b in zip(results, results[1:]):
        assert not np.array_equal(a, b)


def test_rng_state_context_jitted_nested():
    """Regression test: nested RngStateContext seeds jitted PRNG correctly
    at each level."""
    n = 5
    outer_seed = 42
    inner_seed = 123

    with RngStateContext(outer_seed):
        outer_before = _generate_jitted_random_values(n).copy()

    with RngStateContext(outer_seed):
        _generate_jitted_random_values(n)  # consume same values
        with RngStateContext(inner_seed):
            inner_values = _generate_jitted_random_values(n).copy()

    # inner context should produce values determined by inner_seed
    with RngStateContext(inner_seed):
        inner_expected = _generate_jitted_random_values(n)

    np.testing.assert_array_equal(inner_values, inner_expected)

    # outer context should produce values determined by outer_seed
    with RngStateContext(outer_seed):
        outer_expected = _generate_jitted_random_values(n)

    np.testing.assert_array_equal(outer_before, outer_expected)
