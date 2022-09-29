import pickle
import tempfile

import pytest

from hstrat.hstrat import fixed_resolution_algo


@pytest.mark.parametrize("impl", fixed_resolution_algo._PolicySpec_.impls)
@pytest.mark.parametrize(
    "fixed_resolution",
    [
        1,
        2,
        3,
        7,
        42,
        100,
    ],
)
def test_eq(impl, fixed_resolution):
    spec = impl(fixed_resolution)
    assert spec == spec
    assert spec == impl(fixed_resolution)
    assert not spec == impl(fixed_resolution + 1)


@pytest.mark.parametrize(
    "fixed_resolution",
    [
        1,
        2,
        3,
        7,
        42,
        100,
    ],
)
def test_pickle(fixed_resolution):
    original = fixed_resolution_algo.PolicySpec(fixed_resolution)
    with tempfile.TemporaryDirectory() as tmp_path:
        with open(f"{tmp_path}/data", "wb") as tmp_file:
            pickle.dump(original, tmp_file)

        with open(f"{tmp_path}/data", "rb") as tmp_file:
            reconstituted = pickle.load(tmp_file)
            assert reconstituted == original


@pytest.mark.parametrize("impl", fixed_resolution_algo._PolicySpec_.impls)
@pytest.mark.parametrize(
    "fixed_resolution",
    [
        1,
        2,
        3,
        7,
        42,
        100,
    ],
)
def test_GetFixedResolution(impl, fixed_resolution):
    spec = impl(fixed_resolution)
    assert spec.GetFixedResolution() == fixed_resolution


@pytest.mark.parametrize("impl", fixed_resolution_algo._PolicySpec_.impls)
def test_GetAlgoIdentifier(impl):
    fixed_resolution = 1
    spec = impl(fixed_resolution)
    assert spec.GetAlgoIdentifier()


@pytest.mark.parametrize("impl", fixed_resolution_algo._PolicySpec_.impls)
def test_GetAlgoTitle(impl):
    fixed_resolution = 1
    spec = impl(fixed_resolution)
    assert spec.GetAlgoTitle()


@pytest.mark.parametrize("impl", fixed_resolution_algo._PolicySpec_.impls)
def test_repr(impl):
    fixed_resolution = 1
    spec = impl(fixed_resolution)
    assert str(fixed_resolution) in repr(spec)
    assert spec.GetAlgoIdentifier() in repr(spec)


@pytest.mark.parametrize("impl", fixed_resolution_algo._PolicySpec_.impls)
def test_str(impl):
    fixed_resolution = 1
    spec = impl(fixed_resolution)
    assert str(fixed_resolution) in str(spec)
    assert spec.GetAlgoTitle() in str(spec)


@pytest.mark.parametrize(
    "fixed_resolution",
    [
        1,
        2,
        3,
        7,
        42,
        100,
    ],
)
@pytest.mark.parametrize(
    "what",
    [
        lambda x: x.GetFixedResolution(),
        lambda x: x.GetAlgoIdentifier(),
        lambda x: x.GetAlgoTitle(),
        lambda x: repr(x),
        lambda x: str(x),
    ],
)
def test_consistency(fixed_resolution, what):
    assert (
        len(
            {
                what(impl(fixed_resolution))
                for impl in fixed_resolution_algo._PolicySpec_.impls
            }
        )
        == 1
    )
