import pickle
import tempfile

import pytest

from hstrat.hstrat import recency_proportional_resolution_algo


@pytest.mark.parametrize(
    "recency_proportional_resolution",
    [
        0,
        1,
        2,
        3,
        7,
        42,
        97,
        100,
    ],
)
def test_eq(recency_proportional_resolution):
    spec = recency_proportional_resolution_algo.PolicySpec(
        recency_proportional_resolution
    )
    assert spec == spec
    assert spec == recency_proportional_resolution_algo.PolicySpec(
        recency_proportional_resolution
    )
    assert not spec == recency_proportional_resolution_algo.PolicySpec(
        recency_proportional_resolution + 1
    )


@pytest.mark.parametrize(
    "recency_proportional_resolution",
    [
        1,
        2,
        3,
        7,
        42,
        97,
        100,
    ],
)
def test_GetEvalCtor(recency_proportional_resolution):
    # hstrat. is needed for eval()
    from hstrat import hstrat  # noqa

    spec = recency_proportional_resolution_algo.PolicySpec(
        recency_proportional_resolution
    )
    eval_ctor = spec.GetEvalCtor()
    assert eval_ctor.startswith(
        "hstrat.recency_proportional_resolution_algo.PolicySpec("
    )
    assert eval_ctor.endswith(")")
    reconstituted = eval(eval_ctor)  # noqa
    assert spec == reconstituted


@pytest.mark.parametrize(
    "recency_proportional_resolution",
    [
        0,
        1,
        2,
        3,
        7,
        42,
        97,
        100,
    ],
)
def test_pickle(recency_proportional_resolution):
    original = recency_proportional_resolution_algo.PolicySpec(
        recency_proportional_resolution
    )
    with tempfile.TemporaryDirectory() as tmp_path:
        with open(f"{tmp_path}/data", "wb") as tmp_file:
            pickle.dump(original, tmp_file)

        with open(f"{tmp_path}/data", "rb") as tmp_file:
            reconstituted = pickle.load(tmp_file)
            assert reconstituted == original


@pytest.mark.parametrize(
    "recency_proportional_resolution",
    [
        0,
        1,
        2,
        3,
        7,
        42,
        97,
        100,
    ],
)
def test_GetRecencyProportionalResolution(recency_proportional_resolution):
    spec = recency_proportional_resolution_algo.PolicySpec(
        recency_proportional_resolution
    )
    assert (
        spec.GetRecencyProportionalResolution()
        == recency_proportional_resolution
    )


def test_GetAlgoIdentifier():
    recency_proportional_resolution = 1
    spec = recency_proportional_resolution_algo.PolicySpec(
        recency_proportional_resolution
    )
    assert spec.GetAlgoIdentifier()


def test_GetAlgoTitle():
    recency_proportional_resolution = 1
    spec = recency_proportional_resolution_algo.PolicySpec(
        recency_proportional_resolution
    )
    assert spec.GetAlgoTitle()


def test_repr():
    recency_proportional_resolution = 1
    spec = recency_proportional_resolution_algo.PolicySpec(
        recency_proportional_resolution
    )
    assert str(recency_proportional_resolution) in repr(spec)
    assert spec.GetAlgoIdentifier() in repr(spec)


def test_str():
    recency_proportional_resolution = 1
    spec = recency_proportional_resolution_algo.PolicySpec(
        recency_proportional_resolution
    )
    assert str(recency_proportional_resolution) in str(spec)
    assert spec.GetAlgoTitle() in str(spec)
