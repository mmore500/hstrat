import pytest

from hstrat._auxiliary_lib import pairwise, unpairwise


@pytest.mark.parametrize("wrap", [iter, lambda x: x])
def test_unpairwise_empty(wrap):
    assert [*unpairwise(wrap([]))] == []


@pytest.mark.parametrize("wrap", [iter, lambda x: x])
def test_unpairwise_single_pair(wrap):
    assert [*unpairwise(wrap([(1, 2)]))] == [1, 2]


@pytest.mark.parametrize("wrap", [iter, lambda x: x])
def test_unpairwise_multiple_two_pairs(wrap):
    assert [*unpairwise(wrap([(1, 2), (3, 4)]))] == [1, 2, 4]


@pytest.mark.parametrize("wrap", [iter, lambda x: x])
def test_unpairwise_three_pairs(wrap):
    assert [*unpairwise(wrap([(1, 2), (3, 4), (5, 6)]))] == [1, 2, 4, 6]


@pytest.mark.parametrize("wrap", [iter, lambda x: x])
def test_unpairwise_four_pairs(wrap):
    assert [*unpairwise(wrap([(1, 2), (3, 4), (5, 6), (7, 8)]))] == [
        1,
        2,
        4,
        6,
        8,
    ]


@pytest.mark.parametrize("wrap", [iter, list, lambda x: x])
@pytest.mark.parametrize("size", range(20))
def test_unpairwise_inverse_pairwise(wrap, size):
    a = range(size)
    if size == 1:
        assert [*unpairwise(wrap(pairwise(a)))] == []
    else:
        assert [*unpairwise(wrap(pairwise(a)))] == [*a]
