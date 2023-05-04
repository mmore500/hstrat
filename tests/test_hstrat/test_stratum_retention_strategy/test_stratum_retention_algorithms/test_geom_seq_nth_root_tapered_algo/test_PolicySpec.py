import pickle
import tempfile

import pytest

from hstrat.hstrat import geom_seq_nth_root_tapered_algo


@pytest.mark.filterwarnings(
    "ignore:Interspersal set to 1, no bound on MRCA rank estimate uncertainty can be guaranteed."
)
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
def test_eq(degree, interspersal):
    spec = geom_seq_nth_root_tapered_algo.PolicySpec(degree, interspersal)
    assert spec == spec
    assert spec == geom_seq_nth_root_tapered_algo.PolicySpec(
        degree, interspersal
    )
    assert not spec == geom_seq_nth_root_tapered_algo.PolicySpec(
        degree, interspersal + 1
    )
    assert not spec == geom_seq_nth_root_tapered_algo.PolicySpec(
        degree + 1, interspersal
    )
    assert not spec == geom_seq_nth_root_tapered_algo.PolicySpec(
        degree + 1, interspersal + 1
    )


@pytest.mark.filterwarnings(
    "ignore:Interspersal set to 1, no bound on MRCA rank estimate uncertainty can be guaranteed."
)
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
def test_GetEvalCtor(degree, interspersal):
    # hstrat. is needed for eval()
    from hstrat import hstrat  # noqa

    spec = geom_seq_nth_root_tapered_algo.PolicySpec(degree, interspersal)
    eval_ctor = spec.GetEvalCtor()
    assert eval_ctor.startswith(
        "hstrat.geom_seq_nth_root_tapered_algo.PolicySpec("
    )
    assert eval_ctor.endswith(")")
    reconstituted = eval(eval_ctor)  # noqa
    assert spec == reconstituted


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
    original = geom_seq_nth_root_tapered_algo.PolicySpec(degree, interspersal)
    with tempfile.TemporaryDirectory() as tmp_path:
        with open(f"{tmp_path}/data", "wb") as tmp_file:
            pickle.dump(original, tmp_file)

        with open(f"{tmp_path}/data", "rb") as tmp_file:
            reconstituted = pickle.load(tmp_file)
            assert reconstituted == original


@pytest.mark.filterwarnings(
    "ignore:Interspersal set to 1, no bound on MRCA rank estimate uncertainty can be guaranteed."
)
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
def test_GetDegree(degree, interspersal):
    spec = geom_seq_nth_root_tapered_algo.PolicySpec(degree, interspersal)
    assert spec.GetDegree() == degree


@pytest.mark.filterwarnings(
    "ignore:Interspersal set to 1, no bound on MRCA rank estimate uncertainty can be guaranteed."
)
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
def test_GetInterspersal(degree, interspersal):
    spec = geom_seq_nth_root_tapered_algo.PolicySpec(degree, interspersal)
    assert spec.GetInterspersal() == interspersal


def test_GetAlgoIdentifier():
    degree = 1
    interspersal = 2
    spec = geom_seq_nth_root_tapered_algo.PolicySpec(degree, interspersal)
    assert spec.GetAlgoIdentifier()


def test_GetAlgoTitle():
    degree = 1
    interspersal = 2
    spec = geom_seq_nth_root_tapered_algo.PolicySpec(degree, interspersal)
    assert spec.GetAlgoTitle()


def test_repr():
    degree = 1
    interspersal = 2
    spec = geom_seq_nth_root_tapered_algo.PolicySpec(degree, interspersal)
    assert str(degree) in repr(spec)
    assert str(interspersal) in repr(spec)
    assert spec.GetAlgoIdentifier() in repr(spec)


def test_str():
    degree = 1
    interspersal = 2
    spec = geom_seq_nth_root_tapered_algo.PolicySpec(degree, interspersal)
    assert str(degree) in str(spec)
    assert str(interspersal) in str(spec)
    assert spec.GetAlgoTitle() in str(spec)
