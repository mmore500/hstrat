import warnings

import pytest

from hstrat._auxiliary_lib import cast_int_lossless


@pytest.mark.parametrize("action", ["raise", "warn"])
def test_cast_int_lossless_with_int(action: str):
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        assert cast_int_lossless(-42, action) == -42
        assert cast_int_lossless(0, action, context="foo") == 0
        assert cast_int_lossless(10, action) == 10


@pytest.mark.parametrize("action", ["raise", "warn"])
def test_cast_int_lossless_with_float_no_loss(action: str):
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        assert cast_int_lossless(-42.0, action) == -42
        assert cast_int_lossless(0.0, action, context="foo") == 0
        assert cast_int_lossless(10.0, action) == 10


def test_cast_int_lossless_with_loss_warn():
    with pytest.warns(UserWarning):
        assert cast_int_lossless(10.1, "warn") == 10
        assert cast_int_lossless(10.1, "warn", context="foo") == 10


def test_cast_int_lossless_with_loss_raise():
    with pytest.raises(ValueError):
        cast_int_lossless(10.1, "raise")


def test_cast_int_lossless_unrecognized_action():
    with pytest.raises(RuntimeError):
        cast_int_lossless(10.1, "invalid_action")
