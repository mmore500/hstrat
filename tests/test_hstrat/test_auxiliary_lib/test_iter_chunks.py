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


def test_chunking_integers():
    # check if chunking a list of integers returns the correct chunks
    input_list = [1, 2, 3, 4, 5, 6]
    chunk_size = 2
    expected_output = [[1, 2], [3, 4], [5, 6]]
    output = list(iter_chunks(input_list, chunk_size))
    assert output == expected_output


def test_chunking_strings():
    # check if chunking a list of strings returns the correct chunks
    input_list = ["apple", "banana", "cherry", "date"]
    chunk_size = 2
    expected_output = [["apple", "banana"], ["cherry", "date"]]
    output = list(iter_chunks(input_list, chunk_size))
    assert output == expected_output


def test_chunk_size_larger_than_input_list():
    # check if chunking with chunk size larger than the input list returns the
    # input list
    input_list = [1, 2, 3, 4]
    chunk_size = 10
    expected_output = [[1, 2, 3, 4]]
    output = list(iter_chunks(input_list, chunk_size))
    assert output == expected_output


def test_chunk_size_larger_than_input_list_with_start():
    # check if chunking with chunk size larger than the input list returns the
    # input list
    input_list = [1, 2, 3, 4]
    chunk_size = 10
    expected_output = [[2, 3, 4]]
    output = list(iter_chunks(input_list, chunk_size, 1))
    assert output == expected_output


def test_chunk_size_equal_to_one():
    # check if chunking with chunk size equal to 1 returns a list of singleton
    # lists
    input_list = [1, 2, 3, 4]
    chunk_size = 1
    expected_output = [[1], [2], [3], [4]]
    output = list(iter_chunks(input_list, chunk_size))
    assert output == expected_output


def test_start_parameter():
    # check if the `start` parameter works as expected
    input_list = [1, 2, 3, 4, 5, 6]
    chunk_size = 2
    start = 2
    expected_output = [[3, 4], [5, 6]]
    output = list(iter_chunks(input_list, chunk_size, start))
    assert output == expected_output


def test_chunk_size_does_not_divide_input_length():
    # check if chunking with chunk size that does not divide the input list
    # evenly works as expected
    input_list = [1, 2, 3, 4, 5]
    chunk_size = 2
    expected_output = [
        [1, 2],
        [3, 4],
        [
            5,
        ],
    ]
    output = list(iter_chunks(input_list, chunk_size))
    assert output == expected_output


def test_chunk_size_equal_to_input_length():
    # check if chunking with chunk size equal to the input list length returns
    # the input list as a single chunk
    input_list = [1, 2, 3, 4, 5]
    chunk_size = 5
    expected_output = [[1, 2, 3, 4, 5]]
    output = list(iter_chunks(input_list, chunk_size))
    assert output == expected_output


def test_chunk_size_does_not_divide_input_length_with_start():
    # check if chunking with chunk size that does not divide the input list evenly and a non-zero `start` works as expected
    input_list = [1, 2, 3, 4, 5]
    chunk_size = 2
    start = 1
    expected_output = [[2, 3], [4, 5]]
    output = list(iter_chunks(input_list, chunk_size, start))
    assert output == expected_output


def test_chunk_size_equal_to_input_length_with_start():
    # check if chunking with chunk size equal to the input list length and a
    # non-zero `start` works as expected
    input_list = [1, 2, 3, 4, 5]
    chunk_size = 5
    start = 1
    expected_output = [[2, 3, 4, 5]]
    output = list(iter_chunks(input_list, chunk_size, start))
    assert output == expected_output


def test_chunk_size_divides_input_length_with_start_2():
    # check if chunking with chunk size that divides the input list evenly and
    # a `start` of 2 works as expected
    input_list = [1, 2, 3, 4, 5]
    chunk_size = 2
    start = 2
    expected_output = [
        [3, 4],
        [
            5,
        ],
    ]
    output = list(iter_chunks(input_list, chunk_size, start))
    assert output == expected_output


def test_start_equals_length():
    # check if `start` equal to the length of the input list returns an empty
    # list
    input_list = [1, 2, 3, 4, 5]
    chunk_size = 2
    start = len(input_list)
    expected_output = []
    output = list(iter_chunks(input_list, chunk_size, start))
    assert output == expected_output
