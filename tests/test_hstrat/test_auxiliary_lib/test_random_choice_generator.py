import itertools as it

import pytest

from hstrat._auxiliary_lib import random_choice_generator


def test_returns_one_value():
    # Arrange
    values = [1, 2, 3]
    generator = random_choice_generator(values)

    # Act
    result = next(generator)

    # Assert
    assert result in values
    assert isinstance(result, int)


def test_returns_n_values():
    # Arrange
    values = [1, 2, 3]
    n = 5
    generator = random_choice_generator(values)

    # Act
    results = [next(generator) for _ in range(n)]

    # Assert
    assert all(result in values for result in results)
    assert all(isinstance(result, int) for result in results)
    assert set(values) == set(it.islice(generator, 0, 100))


def test_raises_exception_for_empty_list():
    # Arrange
    values = []
    generator = random_choice_generator(values)

    # Act / Assert
    with pytest.raises(IndexError):
        next(generator)


def test_negative_values():
    # Arrange
    values = [-1, 0, 1]
    generator = random_choice_generator(values)

    # Act / Assert
    for val in it.islice(generator, 0, 100):
        assert val in values

    assert set(it.islice(generator, 0, 100)) == set(values)


def test_mixed_values():
    # Arrange
    values = ["string", None, 3, 4.5]
    generator = random_choice_generator(values)

    # Act / Assert
    for val in it.islice(generator, 0, 100):
        assert val in values

    assert set(it.islice(generator, 0, 100)) == set(values)
