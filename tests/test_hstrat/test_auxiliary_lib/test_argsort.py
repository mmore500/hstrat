import pytest

from hstrat._auxiliary_lib import argsort


@pytest.fixture
def seq():
    return [4.0, 2.0, 1.0, 3.0]


def test_argsort(seq):
    expected_output = [2, 1, 3, 0]
    assert argsort(seq) == expected_output


def test_argsort_reverse(seq):
    expected_output = [0, 3, 1, 2]
    assert argsort(seq, reverse=True) == expected_output


def test_argsort_empty_input():
    assert argsort([]) == []


def test_argsort_single_input():
    assert argsort([1]) == [0]
