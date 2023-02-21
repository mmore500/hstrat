import pytest

from hstrat._auxiliary_lib import iter_chunks


@pytest.fixture()
def seq():
    return [1, 2, 3, 4, 5, 6, 7, 8, 9]


def test_chunk_size_one(seq):
    for chunk in iter_chunks(seq, 1):
        assert chunk in [[1], [2], [3], [4], [5], [6], [7], [8], [9]]


def test_chunk_size_two(seq):
    for chunk in iter_chunks(seq, 2):
        assert chunk in [[1, 2], [3, 4], [5, 6], [7, 8], [9]]


def test_chunk_size_greater_than_length(seq):
    for chunk in iter_chunks(seq, 10):
        assert chunk == [1, 2, 3, 4, 5, 6, 7, 8, 9]


def test_empty_sequence():
    assert list(iter_chunks([], 5)) == []


def test_non_list_sequence():
    assert list(iter_chunks("123456", 2)) == ["12", "34", "56"]
