from hstrat._auxiliary_lib import iter_slices


def test_iter_slices_len_seq_0():
    result = list(iter_slices(0, 10))
    assert result == []


def test_iter_slices_len_seq_equals_chunk_size():
    result = list(iter_slices(10, 10))
    assert result == [slice(0, 10)]


def test_iter_slices_len_seq_less_than_chunk_size():
    result = list(iter_slices(5, 10))
    assert result == [slice(0, 10)]


def test_iter_slices_len_seq_greater_than_chunk_size():
    result = list(iter_slices(15, 5))
    assert result == [slice(0, 5), slice(5, 10), slice(10, 15)]


def test_iter_slices_start_greater_than_0():
    result = list(iter_slices(15, 5, 5))
    assert result == [slice(5, 10), slice(10, 15)]


def test_iter_slices_chunk_size_larger_than_input_list():
    result = list(iter_slices(10, 20))
    assert result == [slice(0, 20)]


def test_iter_slices_chunk_size_equal_to_one():
    result = list(iter_slices(10, 1))
    assert result == [
        slice(0, 1),
        slice(1, 2),
        slice(2, 3),
        slice(3, 4),
        slice(4, 5),
        slice(5, 6),
        slice(6, 7),
        slice(7, 8),
        slice(8, 9),
        slice(9, 10),
    ]


def test_iter_slices_start_parameter():
    result = list(iter_slices(12, 5, 2))
    assert result == [slice(2, 7), slice(7, 12)]


def test_iter_slices_chunk_size_does_not_divide_input_length():
    result = list(iter_slices(11, 5))
    assert result == [slice(0, 5), slice(5, 10), slice(10, 15)]


def test_iter_slices_chunk_size_equal_to_input_length():
    result = list(iter_slices(10, 10))
    assert result == [slice(0, 10)]


def test_iter_slices_chunk_size_does_not_divide_input_length_with_start():
    result = list(iter_slices(11, 5, 1))
    assert result == [slice(1, 6), slice(6, 11)]


def test_iter_slices_chunk_size_equal_to_input_length_with_start():
    result = list(iter_slices(10, 10, 1))
    assert result == [slice(1, 11)]


def test_iter_slices_chunk_size_divides_input_length_with_start_2():
    result = list(iter_slices(10, 5, 2))
    assert result == [slice(2, 7), slice(7, 12)]


def test_iter_slices_start_equals_length():
    result = list(iter_slices(10, 5, 10))
    assert result == []
