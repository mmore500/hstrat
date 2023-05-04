import pytest

from hstrat._auxiliary_lib import with_omission


@pytest.mark.parametrize("wrap", [iter, lambda x: x])
def test_with_omission_empty_iterable(wrap):
    iterable = wrap([])
    omit_index = 0
    assert list(with_omission(iterable, omit_index)) == []


@pytest.mark.parametrize("wrap", [iter, lambda x: x])
def test_with_omission_first_index(wrap):
    iterable = wrap([1, 2, 3])
    omit_index = 0
    assert list(with_omission(iterable, omit_index)) == [2, 3]


@pytest.mark.parametrize("wrap", [iter, lambda x: x])
def test_with_omission_middle_index(wrap):
    iterable = wrap([1, 2, 3, 4, 5])
    omit_index = 2
    assert list(with_omission(iterable, omit_index)) == [1, 2, 4, 5]


@pytest.mark.parametrize("wrap", [iter, lambda x: x])
def test_with_omission_last_index(wrap):
    iterable = wrap([1, 2, 3])
    omit_index = 2
    assert list(with_omission(iterable, omit_index)) == [1, 2]


@pytest.mark.parametrize("wrap", [iter, lambda x: x])
def test_with_omission_index_out_of_range(wrap):
    iterable = wrap([1, 2, 3])
    omit_index = 3
    assert list(with_omission(iterable, omit_index)) == [1, 2, 3]


@pytest.mark.parametrize("wrap", [iter, lambda x: x])
def test_with_omission_letters(wrap):
    assert list(with_omission(wrap("abcde"), 2)) == ["a", "b", "d", "e"]
