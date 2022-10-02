from copy import deepcopy
import pickle
import tempfile

import pytest

from hstrat import genome_instrumentation


@pytest.mark.parametrize(
    "impl",
    genome_instrumentation._HereditaryStratum_.impls,
)
def test_deposition_rank(impl):
    assert (
        impl(
            deposition_rank=42,
        ).GetDepositionRank()
        == 42
    )


@pytest.mark.parametrize(
    "impl",
    genome_instrumentation._HereditaryStratum_.impls,
)
def test_differentia_generation(impl):
    original1 = impl(
        deposition_rank=42,
    )
    copy1 = deepcopy(original1)
    original2 = impl(
        deposition_rank=42,
    )

    assert original1 == copy1
    assert original1 != original2
    assert copy1 != original2

    assert original1.GetDifferentia() == copy1.GetDifferentia()
    assert original1.GetDifferentia() != original2.GetDifferentia()
    assert copy1.GetDifferentia() != original2.GetDifferentia()


@pytest.mark.parametrize(
    "impl",
    genome_instrumentation._HereditaryStratum_.impls,
)
def test_equality1(impl):
    assert impl() != impl()
    stratum1 = impl()
    stratum2 = stratum1
    assert stratum1 == stratum2
    assert stratum1 == deepcopy(stratum2)


@pytest.mark.parametrize(
    "impl",
    genome_instrumentation._HereditaryStratum_.impls,
)
def test_equality2(impl):
    def stratum_factory():
        return impl(deposition_rank=42)

    assert stratum_factory() != stratum_factory()
    stratum1 = stratum_factory()
    stratum2 = stratum1
    assert stratum1 == stratum2
    assert stratum1 == deepcopy(stratum2)


@pytest.mark.parametrize(
    "impl",
    genome_instrumentation._HereditaryStratum_.impls,
)
def test_pickle(impl):
    original = impl()
    with tempfile.TemporaryDirectory() as tmp_path:
        with open(f"{tmp_path}/data", "wb") as tmp_file:
            pickle.dump(original, tmp_file)

        with open(f"{tmp_path}/data", "rb") as tmp_file:
            reconstituted = pickle.load(tmp_file)
            assert reconstituted == original
            assert reconstituted != impl()
