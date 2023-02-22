from hstrat._auxiliary_lib import jit, reversed_range


def test_reversed_range_jit():
    reversed_range_jit = jit(nopython=True)(reversed_range)
    # Test with stop value specified
    result = list(reversed_range_jit(1, 5))
    assert result == [*reversed(range(1, 5))]
    result = list(reversed_range_jit(0, 10))
    assert result == [*reversed(range(0, 10))]

    # Test without stop value specified
    result = list(reversed_range_jit(5))
    assert result == [*reversed(range(5))]
    result = list(reversed_range_jit(0))
    assert result == [*reversed(range(0))]


def test_reversed_range_stop_specified():
    # Test with stop value specified
    result = list(reversed_range(1, 5))
    assert result == [*reversed(range(1, 5))]
    result = list(reversed_range(0, 10))
    assert result == [*reversed(range(0, 10))]


def test_reversed_range_no_stop_specified():
    # Test without stop value specified
    result = list(reversed_range(5))
    assert result == [*reversed(range(5))]
    result = list(reversed_range(0))
    assert result == [*reversed(range(0))]


def test_reversed_range_single_element():
    # Test with single-element range
    result = list(reversed_range(5, 6))
    assert result == [*reversed(range(5, 6))]
    result = list(reversed_range(5, 5))
    assert result == [*reversed(range(5, 5))]


def test_reversed_range_negative_values():
    # Test with negative start and stop values
    result = list(reversed_range(-5, -1))
    assert result == [*reversed(range(-5, -1))]


def test_reversed_range_empty_range():
    # Test with an empty range
    result = list(reversed_range(5, 5))
    assert result == [*reversed(range(5, 5))]
    result = list(reversed_range(5, 6))
    assert result == [*reversed(range(5, 6))]
    result = list(reversed_range(0, 0))
    assert result == [*reversed(range(0, 0))]
