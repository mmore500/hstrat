import numpy as np
import pytest

from hstrat._auxiliary_lib import demark


@pytest.mark.parametrize(
    "collection",
    [
        range(20),
        "abcdefghij",
        np.arange(20, dtype=float),
        [{x} for x in range(20)],
        [{3} for x in range(20)],
    ],
)
def test_demark(collection):
    assert len(collection) == len(set(map(demark, collection)))
    for x in collection:
        assert demark(x) == demark(x)
        if isinstance(x, (int, float, str)):
            assert demark(x) == x
