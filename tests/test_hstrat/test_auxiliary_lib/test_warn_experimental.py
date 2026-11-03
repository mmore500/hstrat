import warnings

import pytest

from hstrat._auxiliary_lib import ExperimentalWarning, warn_experimental


@warn_experimental
def _add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


@warn_experimental
class _Adder:
    """Add a number."""

    def __init__(self: "_Adder", a: int) -> None:
        self.a = a

    def __call__(self: "_Adder", b: int) -> int:
        return self.a + b


def test_function(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("HSTRAT_WARN_EXPERIMENTAL_SUPPRESS", raising=False)
    with pytest.warns(ExperimentalWarning, match="_add is experimental"):
        assert _add(1, 2) == 3
    assert _add.__name__ == "_add"
    assert _add.__doc__ == "Add two numbers."


def test_class(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("HSTRAT_WARN_EXPERIMENTAL_SUPPRESS", raising=False)
    with pytest.warns(ExperimentalWarning, match="_Adder is experimental"):
        adder = _Adder(1)
    assert isinstance(adder, _Adder)
    assert adder(2) == 3
    assert _Adder.__doc__ == "Add a number."


def test_suppress(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("HSTRAT_WARN_EXPERIMENTAL_SUPPRESS", "1")
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        assert _add(1, 2) == 3
        assert _Adder(1)(2) == 3
