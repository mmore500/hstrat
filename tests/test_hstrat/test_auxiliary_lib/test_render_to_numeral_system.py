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


def test_render_to_numeral_system(alphabet):
    assert render_to_numeral_system(0, alphabet) == "0"
    assert render_to_numeral_system(1, alphabet) == "1"
    assert render_to_numeral_system(10, alphabet) == "a"
    assert render_to_numeral_system(35, alphabet) == "z"
    assert render_to_numeral_system(36, alphabet) == "10"
    assert render_to_numeral_system(100, alphabet) == "2s"
    assert render_to_numeral_system(123456, alphabet) == "2n9c"


def test_render_and_parse_numeral_system_consistency(alphabet):
    for __ in range(10):
        num = random.randint(0, 1000000)
        base_num = render_to_numeral_system(num, alphabet)
        assert parse_from_numeral_system(base_num, alphabet) == num

    for __ in range(10):
        num_digits = "".join([random.choice(alphabet) for j in range(10)])
        base_num = parse_from_numeral_system(num_digits, alphabet)
        assert render_to_numeral_system(base_num, alphabet) == num_digits


def test_builtin_conversion_operators_consistency():
    for __ in range(100):
        num = random.randint(0, 1000000)
        assert bin(num)[2:] == render_to_numeral_system(num, "01")
        assert hex(num)[2:] == render_to_numeral_system(
            num, "0123456789abcdef"
        )
        assert oct(num)[2:] == render_to_numeral_system(num, string.digits[:8])
        assert str(num) == render_to_numeral_system(num, string.digits)
