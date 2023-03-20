import pytest

from hstrat._auxiliary_lib import raises


def test_raises_success():
    def my_func():
        raise ValueError("test")

    assert raises(my_func, ValueError) == True


def test_raises_failure():
    def my_func():
        raise ValueError("test")

    with pytest.raises(ValueError):
        assert raises(my_func, TypeError) == False


def test_raises_no_exception():
    def my_func():
        return True

    assert raises(my_func, ValueError) == False
