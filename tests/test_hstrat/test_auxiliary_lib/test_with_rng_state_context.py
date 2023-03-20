import random

import pytest

from hstrat._auxiliary_lib import with_rng_state_context


def test_with_rng_state_context_calls_function():
    @with_rng_state_context(seed=123)
    def my_function():
        nonlocal called
        called = True

    called = False
    my_function()
    assert called


def test_with_rng_state_context_sets_seed():
    random.seed(1)
    assert random.getstate() != random.Random(123).getstate()

    @with_rng_state_context(seed=123)
    def my_function():
        assert random.getstate() == random.Random(123).getstate()

    my_function()


def test_with_rng_state_context_works_with_exceptions():
    random.seed(456)
    assert random.getstate() == random.Random(456).getstate()

    @with_rng_state_context(seed=123)
    def my_function():
        assert random.getstate() != random.Random(456).getstate()
        raise ValueError

    with pytest.raises(ValueError):
        my_function()

    assert random.getstate() == random.Random(456).getstate()
