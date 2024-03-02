from hstrat._auxiliary_lib import bytes_swap_bit_order


def test_bytes_swap_bit_order_single_byte():
    input_bytes = b"\x01"  # Binary: 00000001
    expected = b"\x80"  # Binary: 10000000
    assert bytes_swap_bit_order(input_bytes) == expected


def test_bytes_swap_bit_order_multiple_bytes():
    input_bytes = b"\x01\x02"  # Binary: 00000001 00000010
    expected = b"\x80\x40"  # Binary: 10000000 01000000
    assert bytes_swap_bit_order(input_bytes) == expected


def test_bytes_swap_bit_order_zero_byte():
    input_bytes = b"\x00"  # Binary: 00000000
    expected = b"\x00"  # Binary: 00000000
    assert bytes_swap_bit_order(input_bytes) == expected


def test_bytes_swap_bit_order_all_ones_byte():
    input_bytes = b"\xFF"  # Binary: 11111111
    expected = b"\xFF"  # Binary: 11111111
    assert bytes_swap_bit_order(input_bytes) == expected


def test_bytes_swap_bit_order_empty_bytes():
    input_bytes = b""  # Empty byte string
    expected = b""  # Empty byte string
    assert bytes_swap_bit_order(input_bytes) == expected
