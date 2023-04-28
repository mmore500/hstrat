from copy import deepcopy
import itertools as it
import pickle
import tempfile

import pytest

from hstrat import genome_instrumentation, hstrat
from hstrat._auxiliary_lib import is_strictly_increasing


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
def test_lessthan1(impl):
    assert impl() != impl()
    stratum1 = impl()
    stratum2 = stratum1
    assert not (stratum1 < stratum2), (
        str(stratum1),
        str(stratum2),
        stratum1 == stratum2,
    )
    assert not (stratum2 < stratum1)
    assert not (stratum1 < deepcopy(stratum2))


@pytest.mark.parametrize(
    "impl",
    genome_instrumentation._HereditaryStratum_.impls,
)
def test_lessthan2(impl):
    stratum1 = impl(deposition_rank=0)
    stratum2 = impl(deposition_rank=1)
    stratum3 = impl(deposition_rank=2)
    assert (stratum1 < stratum2) != (stratum2 < stratum1)
    assert (stratum1 < stratum3) != (stratum3 < stratum1)
    assert (stratum2 < stratum3) != (stratum3 < stratum2)

    assert sorted([stratum1, stratum2, stratum3]) == sorted(
        [stratum3, stratum2, stratum1]
    )
    assert is_strictly_increasing(sorted([stratum1, stratum2, stratum3]))


def test_lessthan3():
    instances1 = [
        impl(deposition_rank=0)
        for impl in genome_instrumentation._HereditaryStratum_.impls
    ]
    instances2 = [
        impl(deposition_rank=1)
        for impl in genome_instrumentation._HereditaryStratum_.impls
    ]

    assert not any(
        x == y
        for instances in (instances1, instances2)
        for x, y in it.permutations(instances, r=2)
    )
    assert all(
        (x < y) or (y < x)
        for instances in (instances1, instances2)
        for x, y in it.permutations(instances, r=2)
    )

    assert 1 == len({x < y for x, y in it.product(instances1, instances2)})


def test_equality4():
    instances = [
        impl(differentia=i)
        for i, impl in enumerate(
            genome_instrumentation._HereditaryStratum_.impls,
        )
    ]
    for x, y in it.permutations(instances, 2):
        assert x != y


def test_pickle():
    original = hstrat.HereditaryStratum()
    with tempfile.TemporaryDirectory() as tmp_path:
        with open(f"{tmp_path}/data", "wb") as tmp_file:
            pickle.dump(original, tmp_file)

        with open(f"{tmp_path}/data", "rb") as tmp_file:
            reconstituted = pickle.load(tmp_file)
            assert reconstituted == original
            assert reconstituted != hstrat.HereditaryStratum()


def test_str():
    for i, j, k in it.product(range(3), range(3), [None, "asdf", 89.8]):
        assert 1 == len(
            {
                str(impl(differentia=i, deposition_rank=j, annotation=k))
                for impl in genome_instrumentation._HereditaryStratum_.impls
            }
        )
