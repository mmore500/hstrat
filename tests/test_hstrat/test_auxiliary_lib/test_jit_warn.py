import numpy as np
import pytest

from hstrat._auxiliary_lib import jit, jit_prange, jit_warn


def test_jit_warn():
    with pytest.warns(RuntimeWarning, match="hello"):
        jit_warn("hello")


def test_jit_warn_within_jit():
    @jit(nopython=True)
    def warn_if_negative(x: float) -> float:
        if x < 0:
            jit_warn("negative value")
        return abs(x)

    with pytest.warns(RuntimeWarning, match="negative value"):
        assert warn_if_negative(-2.0) == 2.0


def test_jit_warn_within_parallel_jit():
    @jit(nopython=True, parallel=True)
    def abs_all(xs: np.ndarray) -> np.ndarray:
        result = np.empty(len(xs))
        for i in jit_prange(len(xs)):
            if xs[i] < 0:
                jit_warn("negative value")
            result[i] = abs(xs[i])
        return result

    with pytest.warns(RuntimeWarning, match="negative value"):
        result = abs_all(np.array([-1.0, 2.0, -3.0]))
    assert result.tolist() == [1.0, 2.0, 3.0]
