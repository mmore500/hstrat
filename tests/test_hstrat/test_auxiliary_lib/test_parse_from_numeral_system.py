import random
import string

import pytest

from hstrat._auxiliary_lib import (
    parse_from_numeral_system,
    render_to_numeral_system,
)


@pytest.fixture
def alphabet():
    return string.digits + string.ascii_lowercase


def test_parse_from_numeral_system(alphabet):
    assert parse_from_numeral_system("0", alphabet) == 0
    assert parse_from_numeral_system("1", alphabet) == 1
    assert parse_from_numeral_system("a", alphabet) == 10
    assert parse_from_numeral_system("z", alphabet) == 35
    assert parse_from_numeral_system("10", alphabet) == 36
    assert parse_from_numeral_system("2s", alphabet) == 100
    assert parse_from_numeral_system("2n9c", alphabet) == 123456


def test_render_and_parse_numeral_system_consistency(alphabet):
    for __ in range(100):
        num = random.randint(0, 1000000)
        base_num = render_to_numeral_system(num, alphabet)
        assert parse_from_numeral_system(base_num, alphabet) == num

    for __ in range(100):
        test_digits = "".join([random.choice(alphabet) for j in range(10)])
        base_num = parse_from_numeral_system(test_digits, alphabet)
        assert render_to_numeral_system(
            base_num, alphabet
        ) == test_digits.lstrip("0")


def test_hex_parsing():
    assert parse_from_numeral_system("0", "0123456789abcdef") == int("0", 16)
    assert parse_from_numeral_system("1", "0123456789abcdef") == int("1", 16)
    assert parse_from_numeral_system("0a3", "0123456789abcdef") == int(
        "0a3", 16
    )
    assert parse_from_numeral_system("a3", "0123456789abcdef") == int("a3", 16)
    assert parse_from_numeral_system("ff", "0123456789abcdef") == int("ff", 16)


def test_octal_parsing():
    assert parse_from_numeral_system("0", "01234567") == int("0", 8)
    assert parse_from_numeral_system("1", "01234567") == int("1", 8)
    assert parse_from_numeral_system("052", "01234567") == int("052", 8)
    assert parse_from_numeral_system("52", "01234567") == int("52", 8)
    assert parse_from_numeral_system("777", "01234567") == int("777", 8)


def test_binary_parsing():
    assert parse_from_numeral_system("0", "01") == int("0", 2)
    assert parse_from_numeral_system("1", "01") == int("1", 2)
    assert parse_from_numeral_system("0101101", "01") == int("0101101", 2)
    assert parse_from_numeral_system("101101", "01") == int("101101", 2)
    assert parse_from_numeral_system("111", "01") == int("111", 2)


def test_decimal_parsing():
    assert parse_from_numeral_system("0", "0123456789") == int("0", 10)
    assert parse_from_numeral_system("1", "0123456789") == int("1", 10)
    assert parse_from_numeral_system("0123", "0123456789") == int("0123", 10)
    assert parse_from_numeral_system("123", "0123456789") == int("123", 10)
    assert parse_from_numeral_system("456", "0123456789") == int("456", 10)
