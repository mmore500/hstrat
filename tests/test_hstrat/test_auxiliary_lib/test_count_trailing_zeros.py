from hstrat._auxiliary_lib import count_trailing_zeros


def test_no_trailing_zeros():
    assert count_trailing_zeros(0b1) == 0
    assert count_trailing_zeros(-0b1) == 0
    assert count_trailing_zeros(0b11) == 0
    assert count_trailing_zeros(-0b11) == 0


def test_single_trailing_zero():
    assert count_trailing_zeros(0b100110) == 1
    assert count_trailing_zeros(-0b100110) == 1
    assert count_trailing_zeros(0b10) == 1
    assert count_trailing_zeros(-0b10) == 1


def test_multiple_trailing_zeros():
    assert count_trailing_zeros(0b100) == 2
    assert count_trailing_zeros(-0b100) == 2
    assert count_trailing_zeros(0b1100) == 2
    assert count_trailing_zeros(-0b1100) == 2
    assert count_trailing_zeros(0b10100) == 2
    assert count_trailing_zeros(-0b10100) == 2
    assert count_trailing_zeros(0b11100) == 2
    assert count_trailing_zeros(-0b11100) == 2
    assert count_trailing_zeros(0b1000) == 3
    assert count_trailing_zeros(-0b1000) == 3
