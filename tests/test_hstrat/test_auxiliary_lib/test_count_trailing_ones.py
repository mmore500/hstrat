from hstrat._auxiliary_lib import count_trailing_ones


def test_no_trailing_ones():
    assert count_trailing_ones(0b0) == 0
    assert count_trailing_ones(-0b0) == 0
    assert count_trailing_ones(0b100) == 0
    assert count_trailing_ones(-0b100) == 0


def test_single_trailing_one():
    assert count_trailing_ones(0b10111101) == 1
    assert count_trailing_ones(-0b10111101) == 1
    assert count_trailing_ones(0b1) == 1
    assert count_trailing_ones(-0b1) == 1
    assert count_trailing_ones(0b101) == 1
    assert count_trailing_ones(-0b101) == 1


def test_multiple_trailing_ones():
    assert count_trailing_ones(0b11) == 2
    assert count_trailing_ones(-0b11) == 2
    assert count_trailing_ones(0b100011) == 2
    assert count_trailing_ones(-0b100011) == 2
    assert count_trailing_ones(0b1011) == 2
    assert count_trailing_ones(-0b1011) == 2
    assert count_trailing_ones(0b111) == 3
    assert count_trailing_ones(-0b111) == 3
    assert count_trailing_ones(0b100111) == 3
    assert count_trailing_ones(-0b100111) == 3
    assert count_trailing_ones(0b11111) == 5
    assert count_trailing_ones(-0b11111) == 5
