import pytest

from hstrat._auxiliary_lib import raises


def test_raises_success():
    def my_func():
        raise ValueError("test")

    assert raises(my_func, ValueError)


def test_raises_failure():
    def my_func():
        raise ValueError("test")

    with pytest.raises(ValueError):
        assert not raises(my_func, TypeError)


def test_raises_no_exception():
    def my_func():
        return True

    assert not raises(my_func, ValueError)
