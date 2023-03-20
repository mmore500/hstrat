import pytest

from hstrat._auxiliary_lib import deep_listify


def test_deep_listify_not_iterable():
    result = deep_listify(1)
    assert result == 1

    result = deep_listify(None)
    assert result is None

    result = deep_listify(False)
    assert result is False


@pytest.mark.parametrize("wrap", [iter, lambda x: x])
def test_deep_listify_empty_list(wrap):
    result = deep_listify(wrap([]))
    assert result == []


@pytest.mark.parametrize("wrap", [iter, lambda x: x])
def test_deep_listify_empty_list_nested(wrap):
    result = deep_listify(wrap([wrap([])]))
    assert result == [[]]


@pytest.mark.parametrize("wrap", [iter, lambda x: x])
def test_deep_listify_flat_list(wrap):
    result = deep_listify(wrap([1, 2, 3]))
    assert result == [1, 2, 3]


@pytest.mark.parametrize("wrap", [iter, lambda x: x])
def test_deep_listify_nested_list(wrap):
    result = deep_listify(wrap([[1, 2], [3, 4]]))
    assert result == [[1, 2], [3, 4]]


@pytest.mark.parametrize("wrap", [iter, lambda x: x])
def test_deep_listify_nested_tuple(wrap):
    result = deep_listify(wrap([(1, 2), (3, 4)]))
    assert result == [[1, 2], [3, 4]]


@pytest.mark.parametrize("wrap", [iter, lambda x: x])
def test_deep_listify_mixed_nested(wrap):
    result = deep_listify(wrap([1, wrap([2, wrap((3, 4))]), 5]))
    assert result == [1, [2, [3, 4]], 5]


@pytest.mark.parametrize("wrap", [iter, lambda x: x])
def test_deep_listify_iterator(wrap):
    result = deep_listify(wrap(iter([1, 2, 3])))
    assert result == [1, 2, 3]


@pytest.mark.parametrize("wrap", [iter, lambda x: x])
def test_deep_listify_generator(wrap):
    result = deep_listify(wrap((x for x in range(3))))
    assert result == [0, 1, 2]


@pytest.mark.parametrize("wrap", [iter, lambda x: x])
def test_deep_listify_singleton_list_nested(wrap):
    result = deep_listify(wrap([wrap(["asdf"])]))
    assert result == [["asdf"]]
