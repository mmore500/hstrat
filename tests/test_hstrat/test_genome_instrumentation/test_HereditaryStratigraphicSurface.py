from copy import copy, deepcopy
import itertools as it
import random
import types

from downstream import dstream, dsurf
import numpy as np
import pytest

from hstrat import hstrat


@pytest.mark.parametrize(
    "algo", [dstream.steady_algo, dstream.stretched_algo, dstream.tilted_algo]
)
@pytest.mark.parametrize("S", [8, 16, 32, np.empty(32, dtype=np.uint64)])
def test_Clone1(algo: types.ModuleType, S: int):
    original1 = hstrat.HereditaryStratigraphicSurface(dsurf.Surface(algo, S))
    original1_copy1 = deepcopy(original1)
    original1_copy2 = original1.Clone()

    assert original1 == original1_copy1
    assert original1 == original1_copy2
    assert original1_copy1 == original1_copy2

    for first in original1, original1_copy1, original1_copy2:
        for second in original1, original1_copy1, original1_copy2:
            assert hstrat.does_have_any_common_ancestor(first, second)


@pytest.mark.parametrize(
    "algo", [dstream.steady_algo, dstream.stretched_algo, dstream.tilted_algo]
)
@pytest.mark.parametrize("S", [8, 16, 32, np.empty(32, dtype=np.uint64)])
def test_Clone2(algo: types.ModuleType, S: int):
    original2 = hstrat.HereditaryStratigraphicSurface(dsurf.Surface(algo, S))
    original2.DepositStratum()
    original2.DepositStratum()

    original2_copy1 = deepcopy(original2)
    original2_copy2 = original2.Clone()

    for which in original2, original2_copy1, original2_copy2:
        for __ in range(original2.S):
            which.DepositStratum()

    for first in original2, original2_copy1, original2_copy2:
        for second in original2, original2_copy1, original2_copy2:
            assert hstrat.does_have_any_common_ancestor(first, second)


@pytest.mark.parametrize(
    "algo", [dstream.steady_algo, dstream.stretched_algo, dstream.tilted_algo]
)
@pytest.mark.parametrize("S", [8, 16, 32, np.empty(32, dtype=np.uint64)])
def test_Clone3(algo: types.ModuleType, S: int):
    surf = hstrat.HereditaryStratigraphicSurface(dsurf.Surface(algo, S))
    population = [surf.Clone() for __ in range(3)]

    for _generation in range(surf.S):
        _ = _generation

        for f, s in it.combinations(population, 2):
            assert hstrat.does_have_any_common_ancestor(f, s)
            assert (
                hstrat.get_last_common_stratum_between(
                    f,
                    s,
                )
                is not None
            )

        # advance generation
        population[0] = population[0].Clone()
        for individual in population:
            if random.choice([True, False]):
                individual.DepositStratum()


@pytest.mark.parametrize(
    "algo", [dstream.steady_algo, dstream.stretched_algo, dstream.tilted_algo]
)
@pytest.mark.parametrize("S", [8, 16, 32, np.empty(32, dtype=np.uint64)])
def test_Clone4(algo: types.ModuleType, S: int):
    # regression test for bug with tree store cloning
    surf = hstrat.HereditaryStratigraphicSurface(dsurf.Surface(algo, S))
    population = [surf.Clone() for __ in range(3)]

    for _generation in range(surf.S):
        _ = _generation

        for f, s in it.combinations(population, 2):
            assert hstrat.does_have_any_common_ancestor(f, s)
            assert hstrat.get_last_common_stratum_between(f, s) is not None

        # advance generation
        population[0] = population[0].Clone()
        for individual in population:
            if random.choice([True, False]):
                individual.DepositStratum()


@pytest.mark.parametrize(
    "algo", [dstream.steady_algo, dstream.stretched_algo, dstream.tilted_algo]
)
@pytest.mark.parametrize("S", [8, 16, 32, np.empty(32, dtype=np.uint64)])
def test_eq(algo: types.ModuleType, S: int):

    original1 = hstrat.HereditaryStratigraphicSurface(dsurf.Surface(algo, S))
    copy1 = deepcopy(original1)
    copy2 = original1.Clone()
    original2 = hstrat.HereditaryStratigraphicSurface(
        dsurf.Surface(algo, deepcopy(S))
    )

    assert original1 == copy1
    assert original1 == copy2
    assert copy1 == copy2
    assert original1 != original2
    assert copy1 != original2
    assert copy2 != original2

    copy1.DepositStrata(5)
    assert original1 != copy1

    original1.DepositStrata(5)
    assert original1 != copy1


@pytest.mark.parametrize(
    "algo", [dstream.steady_algo, dstream.stretched_algo, dstream.tilted_algo]
)
@pytest.mark.parametrize("S", [32, np.empty(32, dtype=np.uint64)])
def test_annotation(algo: types.ModuleType, S: int):
    surf = hstrat.HereditaryStratigraphicSurface(dsurf.Surface(algo, S))
    population = [surf.Clone() for __ in range(10)]

    for generation in range(surf.S):
        for f, s in it.combinations(population, 2):
            lb, ub = hstrat.calc_rank_of_mrca_bounds_between(
                f, s, prior="arbitrary"
            )
            assert (
                lb
                <= hstrat.get_last_common_stratum_between(
                    f, s
                ).GetDepositionRank()
                < ub
            )
            assert (
                lb
                <= hstrat.get_last_common_stratum_between(
                    s, f
                ).GetDepositionRank()
                < ub
            )

        # advance generation
        random.shuffle(population)
        for target in range(5):
            population[target] = population[-1].Clone()
        for individual in population:
            individual.DepositStratum()


@pytest.mark.parametrize(
    "algo", [dstream.steady_algo, dstream.stretched_algo, dstream.tilted_algo]
)
@pytest.mark.parametrize("S", [8, 16, 32, np.empty(32, dtype=np.uint64)])
def test_GetNumStrataDeposited(algo: types.ModuleType, S: int):
    surf = hstrat.HereditaryStratigraphicSurface(dsurf.Surface(algo, S))
    for i in range(10):
        assert surf.GetNumStrataDeposited() == i + surf.S + 1
        surf.DepositStratum()


@pytest.mark.parametrize(
    "algo", [dstream.steady_algo, dstream.stretched_algo, dstream.tilted_algo]
)
@pytest.mark.parametrize("S", [8, 16, 32, np.empty(32, dtype=np.uint64)])
def test_CloneDescendant(algo: types.ModuleType, S: int):
    surf = hstrat.HereditaryStratigraphicSurface(dsurf.Surface(algo, S))
    assert surf.GetNumStrataDeposited() == surf.S + 1
    descendant = surf.CloneDescendant()
    assert descendant.GetNumStrataDeposited() == surf.S + 2
    assert hstrat.does_have_any_common_ancestor(descendant, surf)
    assert surf.GetNumStrataDeposited() == surf.S + 1


@pytest.mark.parametrize(
    "algo", [dstream.steady_algo, dstream.stretched_algo, dstream.tilted_algo]
)
@pytest.mark.parametrize("S", [8, 16, 32, np.empty(32, dtype=np.uint64)])
def test_IterRetainedStrata(algo: types.ModuleType, S: int):
    surf = hstrat.HereditaryStratigraphicSurface(
        dsurf.Surface(algo, S),
    )
    for __ in range(20):
        surf.DepositStratum()
        assert [*surf.IterRetainedStrata()] == [
            surf.GetStratumAtColumnIndex(index)
            for index in range(surf.GetNumStrataRetained())
        ]


@pytest.mark.parametrize(
    "algo", [dstream.steady_algo, dstream.stretched_algo, dstream.tilted_algo]
)
@pytest.mark.parametrize("S", [8, 16, 32, np.empty(32, dtype=np.uint64)])
def test_IterRetainedDifferentia(algo: types.ModuleType, S: int):
    surf = hstrat.HereditaryStratigraphicSurface(
        dsurf.Surface(algo, S),
    )
    for __ in range(20):
        surf.DepositStratum()
        assert [*surf.IterRetainedDifferentia()] == [
            surf.GetStratumAtColumnIndex(index).GetDifferentia()
            for index in range(surf.GetNumStrataRetained())
        ]


def test_GetColumnIndexOfRank():
    assert (
        hstrat.HereditaryStratigraphicSurface(
            dsurf.Surface(dstream.steady_algo, 128)
        ).GetColumnIndexOfRank(1)
        is None
    )


def test_GetColumnIndexOfRank2():
    surf = hstrat.HereditaryStratigraphicSurface(
        dsurf.Surface(dstream.steady_algo, 32)
    )
    surf.DepositStrata(64)
    col_indices = [
        surf.GetColumnIndexOfRank(x) for x in surf.IterRetainedRanks()
    ]
    assert all(x is not None for x in col_indices)
    assert all(
        first < second for first, second in zip(col_indices, col_indices[1:])
    )


@pytest.mark.parametrize(
    "algo", [dstream.steady_algo, dstream.stretched_algo, dstream.tilted_algo]
)
@pytest.mark.parametrize("S", [8, 16, 32, np.empty(32, dtype=np.uint64)])
def test_GetStratumAtRank(algo: types.ModuleType, S: int):
    surf = hstrat.HereditaryStratigraphicSurface(
        dsurf.Surface(algo, S),
    )
    for __ in range(20):
        for rank, stratum in zip(
            surf.IterRetainedRanks(),
            surf.IterRetainedStrata(),
        ):
            assert surf.GetStratumAtRank(rank) == stratum
        surf.DepositStratum()

    assert (
        hstrat.HereditaryStratigraphicSurface(
            dsurf.Surface(dstream.steady_algo, 128)
        ).GetStratumAtRank(1)
        is None
    )


@pytest.mark.parametrize(
    "algo", [dstream.steady_algo, dstream.stretched_algo, dstream.tilted_algo]
)
@pytest.mark.parametrize("S", [8, 16, 32, np.empty(32, dtype=np.uint64)])
def test_DepositStrata_zero(algo: types.ModuleType, S: int):
    surf = hstrat.HereditaryStratigraphicSurface(dsurf.Surface(algo, S))
    for __ in range(20):
        clone = surf.Clone()
        surf.DepositStrata(0)
        assert clone == surf
        surf.DepositStratum()


@pytest.mark.parametrize(
    "algo", [dstream.steady_algo, dstream.stretched_algo, dstream.tilted_algo]
)
@pytest.mark.parametrize("S", [8, 16, 32, np.empty(32, dtype=np.uint64)])
def test_DepositStrata_one(algo: types.ModuleType, S: int):
    c1 = hstrat.HereditaryStratigraphicSurface(dsurf.Surface(algo, S))
    c2 = c1.Clone()

    for __ in range(20):
        c1.DepositStrata(1)
        c2.DepositStratum()
        assert all(
            a == b
            for a, b in it.zip_longest(
                c1.IterRetainedRanks(),
                c2.IterRetainedRanks(),
            )
        )
        assert c1.GetNumStrataRetained() == c2.GetNumStrataRetained()
        assert c1.GetNumStrataDeposited() == c2.GetNumStrataDeposited()


@pytest.mark.parametrize(
    "algo", [dstream.steady_algo, dstream.stretched_algo, dstream.tilted_algo]
)
@pytest.mark.parametrize("S", [8, 16, 32, np.empty(32, dtype=np.uint64)])
def test_DepositStrata_several(algo: types.ModuleType, S: int):
    c1 = hstrat.HereditaryStratigraphicSurface(dsurf.Surface(algo, S))
    c2 = c1.Clone()

    for __ in range(20):
        step = random.randrange(10)
        c1.DepositStrata(step)
        for __ in range(step):
            c2.DepositStratum()
        assert all(
            a == b
            for a, b in it.zip_longest(
                c1.IterRetainedRanks(),
                c2.IterRetainedRanks(),
            )
        )
        assert c1.GetNumStrataRetained() == c2.GetNumStrataRetained()
        assert c1.GetNumStrataDeposited() == c2.GetNumStrataDeposited()


@pytest.mark.parametrize(
    "algo", [dstream.steady_algo, dstream.stretched_algo, dstream.tilted_algo]
)
@pytest.mark.parametrize("S", [8, 16, 32, np.empty(32, dtype=np.uint64)])
def test_IterRankDifferentiaZip(algo: types.ModuleType, S: int):
    c1 = hstrat.HereditaryStratigraphicSurface(dsurf.Surface(algo, S))

    for __ in range(100):
        c1.DepositStratum()
        assert [*c1.IterRankDifferentiaZip()] == [
            *zip(c1.IterRetainedRanks(), c1.IterRetainedDifferentia())
        ]
        iter_ = c1.IterRankDifferentiaZip(copyable=True)
        iter_copy = copy(iter_)
        next(iter_copy)
        assert [*iter_copy] == [
            *zip(c1.IterRetainedRanks(), c1.IterRetainedDifferentia())
        ][1:]
        assert [*iter_] == [
            *zip(c1.IterRetainedRanks(), c1.IterRetainedDifferentia())
        ]


def test_predeposit_strata():
    assert (
        hstrat.HereditaryStratigraphicSurface(
            dsurf.Surface(dstream.steady_algo, 128),
            predeposit_strata=0,
        ).GetNumStrataDeposited()
        == 128 + 0
    )
    assert (
        hstrat.HereditaryStratigraphicSurface(
            dsurf.Surface(dstream.steady_algo, 128),
            predeposit_strata=1,
        ).GetNumStrataDeposited()
        == 128 + 1
    )
    assert (
        hstrat.HereditaryStratigraphicSurface(
            dsurf.Surface(dstream.steady_algo, 128),
            predeposit_strata=42,
        ).GetNumStrataDeposited()
        == 128 + 42
    )


def test_CloneNthDescendant_zero():
    surf = hstrat.HereditaryStratigraphicSurface(
        dsurf.Surface(dstream.steady_algo, 128)
    )
    assert surf.GetNumStrataDeposited() == 128 + 1
    descendant = surf.CloneNthDescendant(0)
    assert surf is not descendant
    assert descendant.GetNumStrataDeposited() == 128 + 1
    assert hstrat.does_have_any_common_ancestor(descendant, surf)
    assert surf.GetNumStrataDeposited() == 128 + 1


def test_CloneNthDescendant_one():
    surf = hstrat.HereditaryStratigraphicSurface(
        dsurf.Surface(dstream.steady_algo, 128)
    )
    assert surf.GetNumStrataDeposited() == 128 + 1
    descendant = surf.CloneNthDescendant(num_stratum_depositions=1)
    assert surf is not descendant
    assert descendant.GetNumStrataDeposited() == 128 + 2
    assert hstrat.does_have_any_common_ancestor(descendant, surf)
    assert surf.GetNumStrataDeposited() == 128 + 1


def test_CloneNthDescendant_two():
    surf = hstrat.HereditaryStratigraphicSurface(
        dsurf.Surface(dstream.steady_algo, 128)
    )
    assert surf.GetNumStrataDeposited() == 128 + 1
    descendant = surf.CloneNthDescendant(num_stratum_depositions=2)
    assert surf is not descendant
    assert descendant.GetNumStrataDeposited() == 128 + 3
    assert hstrat.does_have_any_common_ancestor(descendant, surf)
    assert surf.GetNumStrataDeposited() == 128 + 1


def test_StorageIndex():
    surf = hstrat.HereditaryStratigraphicSurface(
        dsurf.Surface(dstream.steady_algo, 32)
    )
    surf.DepositStrata(64)
    for i in range(64):
        idx = surf.GetStorageIndexOfRank(i)
        if idx is not None:
            assert (
                dstream.steady_algo.assign_storage_site(surf.S, i + surf.S)
                == idx
            )
            assert surf.GetRankAtStorageIndex(idx) == i


@pytest.mark.parametrize(
    "algo", [dstream.steady_algo, dstream.stretched_algo, dstream.tilted_algo]
)
@pytest.mark.parametrize("S", [8, 16, 32, np.empty(32, dtype=np.uint64)])
@pytest.mark.parametrize("n", [1, 5, 25, 100])
def test_GetNumStrataDiscarded(algo: types.ModuleType, S: int, n: int):
    surf = hstrat.HereditaryStratigraphicSurface(dsurf.Surface(algo, S))
    assert not surf.HasDiscardedStrata()
    surf.DepositStrata(n)
    assert surf.HasDiscardedStrata() == (n + 1 > surf.S)
    assert surf.GetNumDiscardedStrata() == max(n + 1 - surf.S, 0)


@pytest.mark.parametrize(
    "algo", [dstream.steady_algo, dstream.stretched_algo, dstream.tilted_algo]
)
@pytest.mark.parametrize("S", [8, 16, 32, np.empty(32, dtype=np.uint64)])
@pytest.mark.parametrize("n", [1, 5, 25, 100])
def test_FromHex(algo: types.ModuleType, S: int, n: int):
    surf = hstrat.HereditaryStratigraphicSurface(dsurf.Surface(algo, S))
    surf.DepositStrata(n)
    assert (
        surf.from_hex(
            surf.to_hex(),
            dstream_algo=algo,
            dstream_T_bitoffset=0,
            dstream_T_bitwidth=32,
            dstream_storage_bitoffset=32,
            dstream_storage_bitwidth=surf.S
            * surf.GetStratumDifferentiaBitWidth(),
            dstream_S=surf.S,
        )
        == surf
    )
