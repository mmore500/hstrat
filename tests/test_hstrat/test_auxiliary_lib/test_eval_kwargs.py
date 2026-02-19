import pytest

from hstrat._auxiliary_lib import eval_kwargs


def test_empty():
    assert eval_kwargs([]) == {}


def test_single_string():
    assert eval_kwargs(["key='value'"]) == {"key": "value"}


def test_single_int():
    assert eval_kwargs(["x=42"]) == {"x": 42}


def test_single_float():
    assert eval_kwargs(["origin_time=0.0"]) == {"origin_time": 0.0}


def test_single_none():
    assert eval_kwargs(["infer_schema_length=None"]) == {
        "infer_schema_length": None,
    }


def test_multiple():
    result = eval_kwargs(["x=1", "y='hello'", "z=None"])
    assert result == {"x": 1, "y": "hello", "z": None}


def test_bool():
    assert eval_kwargs(["flag=True"]) == {"flag": True}
    assert eval_kwargs(["flag=False"]) == {"flag": False}


def test_invalid_raises():
    with pytest.raises(ValueError, match="Failed to parse"):
        eval_kwargs(["not valid python!!!"])
