from copy import copy

import pandas as pd
import pytest

from hstrat._auxiliary_lib import CopyableSeriesItemsIter


@pytest.fixture
def sample_series():
    return pd.Series([10, 20, 30, 40], index=["a", "b", "c", "d"])


def test_copyable_series_items_iter_initial_position(sample_series):
    c = CopyableSeriesItemsIter(sample_series)
    assert c._position == 0


def test_copyable_series_items_iter_next_returns_tuple(sample_series):
    c = CopyableSeriesItemsIter(sample_series)
    assert isinstance(next(c), tuple)


def test_copyable_series_items_iter_iteration(sample_series):
    c = CopyableSeriesItemsIter(sample_series)
    items = list(c)
    assert len(items) == len(sample_series)
    assert items[0] == ("a", 10)
    assert items[-1] == ("d", 40)


def test_copyable_series_items_iter_empty_series():
    empty_series = pd.Series(dtype=int)
    c = CopyableSeriesItemsIter(empty_series)
    with pytest.raises(StopIteration):
        next(c)


def test_copyable_series_items_iter_copy1():
    s = pd.Series([1, 2, 3])
    c = CopyableSeriesItemsIter(s)
    c_copy = copy(c)
    assert isinstance(c_copy, CopyableSeriesItemsIter)
    assert list(c_copy) == list(c)


def test_copyable_series_items_iter_copy2():
    s = pd.Series([1, 2, 3])
    c = CopyableSeriesItemsIter(s)
    next(c)
    c_copy = copy(c)
    assert isinstance(c_copy, CopyableSeriesItemsIter)
    assert list(c_copy) == list(c)
