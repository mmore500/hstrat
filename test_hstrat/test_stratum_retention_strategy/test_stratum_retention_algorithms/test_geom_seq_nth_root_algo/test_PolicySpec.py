import pickle
import tempfile

import pytest

from hstrat.hstrat import geom_seq_nth_root_algo


@pytest.mark.parametrize("impl", geom_seq_nth_root_algo._PolicySpec_.impls)
@pytest.mark.parametrize(
    "degree",
    [
        1,
        2,
        3,
        7,
        9,
        42,
        97,
        100,
    ],
)
@pytest.mark.parametrize(
    "interspersal",
    [
        1,
        2,
        5,
    ],
)
def test_eq(impl, degree, interspersal):
    spec = impl(degree, interspersal)
    assert spec == spec
    assert spec == impl(degree, interspersal)
    assert not spec == impl(degree, interspersal + 1)
    assert not spec == impl(degree + 1, interspersal)
    assert not spec == impl(degree + 1, interspersal + 1)


@pytest.mark.parametrize(
    "degree",
    [
        1,
        2,
        3,
        7,
        9,
        42,
        97,
        100,
    ],
)
@pytest.mark.parametrize(
    "interspersal",
    [
        1,
        2,
        5,
    ],
)
def test_pickle(degree, interspersal):
    original = geom_seq_nth_root_algo.PolicySpec(degree, interspersal)
    with tempfile.TemporaryDirectory() as tmp_path:
        with open(f"{tmp_path}/data", "wb") as tmp_file:
            pickle.dump(original, tmp_file)

        with open(f"{tmp_path}/data", "rb") as tmp_file:
            reconstituted = pickle.load(tmp_file)
            assert reconstituted == original


@pytest.mark.parametrize("impl", geom_seq_nth_root_algo._PolicySpec_.impls)
@pytest.mark.parametrize(
    "degree",
    [
        1,
        2,
        3,
        7,
        9,
        42,
        97,
        100,
    ],
)
@pytest.mark.parametrize(
    "interspersal",
    [
        1,
        2,
        5,
    ],
)
def test_GetDegree(impl, degree, interspersal):
    spec = impl(degree, interspersal)
    assert spec.GetDegree() == degree


@pytest.mark.parametrize("impl", geom_seq_nth_root_algo._PolicySpec_.impls)
@pytest.mark.parametrize(
    "degree",
    [
        1,
        2,
        3,
        7,
        9,
        42,
        97,
        100,
    ],
)
@pytest.mark.parametrize(
    "interspersal",
    [
        1,
        2,
        5,
    ],
)
def test_GetIterspersal(impl, degree, interspersal):
    spec = impl(degree, interspersal)
    assert spec.GetInterspersal() == interspersal


@pytest.mark.parametrize("impl", geom_seq_nth_root_algo._PolicySpec_.impls)
def test_GetAlgoIdentifier(impl):
    degree = 1
    interspersal = 2
    spec = impl(degree, interspersal)
    assert spec.GetAlgoIdentifier()


@pytest.mark.parametrize("impl", geom_seq_nth_root_algo._PolicySpec_.impls)
def test_GetAlgoTitle(impl):
    degree = 1
    interspersal = 2
    spec = impl(degree, interspersal)
    assert spec.GetAlgoTitle()


@pytest.mark.parametrize("impl", geom_seq_nth_root_algo._PolicySpec_.impls)
def test_repr(impl):
    degree = 1
    interspersal = 2
    spec = impl(degree, interspersal)
    assert str(degree) in repr(spec)
    assert str(interspersal) in repr(spec)
    assert spec.GetAlgoIdentifier() in repr(spec)


@pytest.mark.parametrize("impl", geom_seq_nth_root_algo._PolicySpec_.impls)
def test_str(impl):
    degree = 1
    interspersal = 2
    spec = impl(degree, interspersal)
    assert str(degree) in str(spec)
    assert str(interspersal) in str(spec)
    assert spec.GetAlgoTitle() in str(spec)


@pytest.mark.parametrize(
    "degree",
    [
        1,
        2,
        3,
        7,
        9,
        42,
        97,
        100,
    ],
)
@pytest.mark.parametrize(
    "interspersal",
    [
        1,
        2,
        5,
    ],
)
@pytest.mark.parametrize(
    "what",
    [
        lambda x: x.GetDegree(),
        lambda x: x.GetInterspersal(),
        lambda x: x.GetAlgoIdentifier(),
        lambda x: x.GetAlgoTitle(),
        lambda x: repr(x),
        lambda x: str(x),
    ],
)
def test_consistency(degree, interspersal, what):
    assert (
        len(
            {
                what(impl(degree, interspersal))
                for impl in geom_seq_nth_root_algo._PolicySpec_.impls
            }
        )
        == 1
    )
