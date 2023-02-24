import pandas as pd
import pytest

from hstrat import hstrat
from hstrat.juxtaposition._impl._dispatch_impl import dispatch_impl


def test_dispatch_impl_column():
    target = hstrat.HereditaryStratigraphicColumn()
    impl_module = dispatch_impl(target, target)
    assert impl_module.__name__.endswith("_impl_column")


def test_dispatch_impl_specimen():
    target = hstrat.HereditaryStratigraphicSpecimen(
        pd.Series([], dtype="int8"), 8
    )
    impl_module = dispatch_impl(target, target)
    assert impl_module.__name__.endswith("_impl_specimen")


def test_dispatch_impl_invalid_input():
    target = "invalid"
    with pytest.raises(TypeError):
        dispatch_impl(target, target)
