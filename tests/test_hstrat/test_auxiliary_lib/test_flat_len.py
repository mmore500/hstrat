import pytest

from hstrat._auxiliary_lib import flat_len


def test_flat_len_not_iterable():
    result = flat_len(11)
    assert result == 1

    result = flat_len(None)
    assert result == 1

    result = flat_len(False)
    assert result == 1


@pytest.mark.parametrize("wrap", [iter, lambda x: x])
def test_flat_len_empty_list(wrap):
    result = flat_len(wrap([]))
    assert result == 0


@pytest.mark.parametrize("wrap", [iter, lambda x: x])
def test_flat_len_empty_list_nested(wrap):
    result = flat_len(wrap([wrap([])]))
    assert result == 0


@pytest.mark.parametrize("wrap", [iter, lambda x: x])
def test_flat_len_flat_list_singleton(wrap):
    result = flat_len(wrap([1]))
    assert result == 1


@pytest.mark.parametrize("wrap", [iter, lambda x: x])
def test_flat_len_flat_list(wrap):
    result = flat_len(wrap([1, 2, 3]))
    assert result == 3


@pytest.mark.parametrize("wrap", [iter, lambda x: x])
def test_flat_len_nested_list(wrap):
    result = flat_len(wrap([[1, 2], [3, 4]]))
    assert result == 4


@pytest.mark.parametrize("wrap", [iter, lambda x: x])
def test_flat_len_nested_tuple(wrap):
    result = flat_len(wrap([(1, 2), (3, 4)]))
    assert result == 4


@pytest.mark.parametrize("wrap", [iter, lambda x: x])
def test_flat_len_mixed_nested(wrap):
    result = flat_len(wrap([1, wrap([2, wrap((3, 4))]), 5]))
    assert result == 5


@pytest.mark.parametrize("wrap", [iter, lambda x: x])
def test_flat_len_iterator(wrap):
    result = flat_len(wrap(iter([1, 2, 3])))
    assert result == 3


@pytest.mark.parametrize("wrap", [iter, lambda x: x])
def test_flat_len_generator(wrap):
    result = flat_len(wrap((x for x in range(3))))
    assert result == 3


@pytest.mark.parametrize("wrap", [iter, lambda x: x])
def test_flat_len_singleton_list_nested(wrap):
    result = flat_len(wrap([wrap(["asdf"])]))
    assert result == 4
