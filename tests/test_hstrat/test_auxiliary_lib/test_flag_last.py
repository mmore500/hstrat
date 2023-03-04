from typing import List

import pytest

from hstrat._auxiliary_lib import flag_last


@pytest.fixture
def sample_data() -> List[int]:
    return [1, 2, 3, 4, 5]


def test_empty_input():
    result = [*flag_last([])]
    assert result == []


def test_single_item_input():
    result = [*flag_last([1])]
    assert result == [(True, 1)]


def test_two_item_input():
    result = [*flag_last([1, 2])]
    assert result == [(False, 1), (True, 2)]


def test_even_input(sample_data):
    result = [*flag_last(sample_data[:4])]
    expected = [(False, 1), (False, 2), (False, 3), (True, 4)]
    assert result == expected


def test_odd_input(sample_data):
    result = [*flag_last(sample_data)]
    expected = [(False, 1), (False, 2), (False, 3), (False, 4), (True, 5)]
    assert result == expected


def test_iterator_input(sample_data):
    result = [*flag_last(iter(sample_data))]
    expected = [(False, 1), (False, 2), (False, 3), (False, 4), (True, 5)]
    assert result == expected


def test_mixed_type_input():
    result = [*flag_last([1, 2, "a"])]
    expected = [(False, 1), (False, 2), (True, "a")]
    assert result == expected
