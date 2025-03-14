from copy import copy, deepcopy
import itertools as it
import pickle
import random
import tempfile
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
    original2 = hstrat.HereditaryStratigraphicSurface(
        dsurf.Surface(algo, S)
    )
    original2.DepositStratum()
    original2.DepositStratum()

    original2_copy1 = deepcopy(original2)
    original2_copy2 = original2.Clone()

    for which in original2, original2_copy1, original2_copy2:
        for __ in range(S if isinstance(S, int) else len(S)):
            which.DepositStratum()

    for first in original2, original2_copy1, original2_copy2:
        for second in original2, original2_copy1, original2_copy2:
            assert hstrat.does_have_any_common_ancestor(first, second)



@pytest.mark.parametrize(
    "algo", [dstream.steady_algo, dstream.stretched_algo, dstream.tilted_algo]
)
@pytest.mark.parametrize("S", [8, 16, 32, np.empty(32, dtype=np.uint64)])
def test_Clone3(algo: types.ModuleType, S: int):
    column = hstrat.HereditaryStratigraphicSurface(
        dsurf.Surface(algo, S)
    )
    population = [column.Clone() for __ in range(3)]

    for _generation in range(S if isinstance(S, int) else len(S)):
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
    column = hstrat.HereditaryStratigraphicSurface(
        dsurf.Surface(algo, S)
    )
    population = [column.Clone() for __ in range(3)]

    for _generation in range(S if isinstance(S, int) else len(S)):
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

    original1 = hstrat.HereditaryStratigraphicSurface(
        dsurf.Surface(algo, S)
    )
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
    column = hstrat.HereditaryStratigraphicSurface(
        dsurf.Surface(algo, S)
    )
    population = [column.Clone() for __ in range(10)]

    for generation in range(S if isinstance(S, int) else len(S)):
        for f, s in it.combinations(population, 2):
            lb, ub = hstrat.calc_rank_of_mrca_bounds_between(
                f, s, prior="arbitrary"
            )
            assert (
                lb
                <= hstrat.get_last_common_stratum_between(f, s).GetDepositionRank()
                < ub
            )
            assert (
                lb
                <= hstrat.get_last_common_stratum_between(s, f).GetDepositionRank()
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
    column = hstrat.HereditaryStratigraphicSurface(
        dsurf.Surface(algo, S)
    )
    for i in range(10):
        assert column.GetNumStrataDeposited() == i + (S if isinstance(S, int) else len(S))
        column.DepositStratum()


@pytest.mark.parametrize(
    "algo", [dstream.steady_algo, dstream.stretched_algo, dstream.tilted_algo]
)
@pytest.mark.parametrize("S", [8, 16, 32, np.empty(32, dtype=np.uint64)])
def test_CloneDescendant(algo: types.ModuleType, S: int):
    column = hstrat.HereditaryStratigraphicSurface(
        dsurf.Surface(algo, S)
    )
    assert column.GetNumStrataDeposited() == (S if isinstance(S, int) else len(S))
    descendant = column.CloneDescendant()
    assert descendant.GetNumStrataDeposited() == (S if isinstance(S, int) else len(S)) + 1
    assert hstrat.does_have_any_common_ancestor(descendant, column)
    assert column.GetNumStrataDeposited() == (S if isinstance(S, int) else len(S))


@pytest.mark.parametrize(
    "algo", [dstream.steady_algo, dstream.stretched_algo, dstream.tilted_algo]
)
@pytest.mark.parametrize("S", [8, 16, 32, np.empty(32, dtype=np.uint64)])
def test_IterRetainedStrata(algo: types.ModuleType, S: int):
    column = hstrat.HereditaryStratigraphicSurface(
        dsurf.Surface(algo, S),
    )
    for __ in range(20):
        column.DepositStratum()
        assert [*column.IterRetainedStrata()] == [
            column.GetStratumAtColumnIndex(index)
            for index in range(column.GetNumStrataRetained())
        ]


@pytest.mark.parametrize(
    "algo", [dstream.steady_algo, dstream.stretched_algo, dstream.tilted_algo]
)
@pytest.mark.parametrize("S", [8, 16, 32, np.empty(32, dtype=np.uint64)])
def test_IterRetainedDifferentia(algo: types.ModuleType, S: int):
    column = hstrat.HereditaryStratigraphicSurface(
        dsurf.Surface(algo, S),
    )
    for __ in range(20):
        column.DepositStratum()
        assert [*column.IterRetainedDifferentia()] == [
            column.GetStratumAtColumnIndex(index).GetDifferentia()
            for index in range(column.GetNumStrataRetained())
        ]


def test_GetColumnIndexOfRank():
    assert (
        hstrat.HereditaryStratigraphicSurface(
            dsurf.Surface(dstream.steady_algo, 128)
        ).GetColumnIndexOfRank(1) is None
    )


@pytest.mark.parametrize(
    "algo", [dstream.steady_algo, dstream.stretched_algo, dstream.tilted_algo]
)
@pytest.mark.parametrize("S", [8, 16, 32, np.empty(32, dtype=np.uint64)])
def test_GetStratumAtRank(algo: types.ModuleType, S: int):
    column = hstrat.HereditaryStratigraphicSurface(
        dsurf.Surface(algo, S),
    )
    for __ in range(20):
        for rank, stratum in zip(
            column.IterRetainedRanks(),
            column.IterRetainedStrata(),
        ):
            assert column.GetStratumAtRank(rank) == stratum
        column.DepositStratum()

    assert hstrat.HereditaryStratigraphicSurface(
        dsurf.Surface(dstream.steady_algo, 128)
    ).GetStratumAtRank(1) is None


@pytest.mark.parametrize(
    "algo", [dstream.steady_algo, dstream.stretched_algo, dstream.tilted_algo]
)
@pytest.mark.parametrize("S", [8, 16, 32, np.empty(32, dtype=np.uint64)])
def test_DepositStrata_zero(algo: types.ModuleType, S: int):
    column = hstrat.HereditaryStratigraphicSurface(
        dsurf.Surface(algo, S)
    )
    for __ in range(20):
        clone = column.Clone()
        column.DepositStrata(0)
        assert clone == column
        column.DepositStratum()



@pytest.mark.parametrize(
    "algo", [dstream.steady_algo, dstream.stretched_algo, dstream.tilted_algo]
)
@pytest.mark.parametrize("S", [8, 16, 32, np.empty(32, dtype=np.uint64)])
def test_DepositStrata_one(algo: types.ModuleType, S: int):
    c1 = hstrat.HereditaryStratigraphicSurface(
        dsurf.Surface(algo, S)
    )
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
    c1 = hstrat.HereditaryStratigraphicSurface(
        dsurf.Surface(algo, S)
    )
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
    c1 = hstrat.HereditaryStratigraphicSurface(
        dsurf.Surface(algo, S)
    )

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


def test_CloneNthDescendant_zero():
    column = hstrat.HereditaryStratigraphicSurface(
        dsurf.Surface(dstream.steady_algo, 128)
    )
    assert column.GetNumStrataDeposited() == 128
    descendant = column.CloneNthDescendant(0)
    assert column is not descendant
    assert descendant.GetNumStrataDeposited() == 128
    assert hstrat.does_have_any_common_ancestor(descendant, column)
    assert column.GetNumStrataDeposited() == 128


def test_CloneNthDescendant_one():
    column = hstrat.HereditaryStratigraphicSurface(
        dsurf.Surface(dstream.steady_algo, 128)
    )
    assert column.GetNumStrataDeposited() == 128
    descendant = column.CloneNthDescendant(num_stratum_depositions=1)
    assert column is not descendant
    assert descendant.GetNumStrataDeposited() == 128 + 1
    assert hstrat.does_have_any_common_ancestor(descendant, column)
    assert column.GetNumStrataDeposited() == 128


def test_CloneNthDescendant_two():
    column = hstrat.HereditaryStratigraphicSurface(
        dsurf.Surface(dstream.steady_algo, 128)
    )
    assert column.GetNumStrataDeposited() == 128
    descendant = column.CloneNthDescendant(num_stratum_depositions=2)
    assert column is not descendant
    assert descendant.GetNumStrataDeposited() == 128 + 2
    assert hstrat.does_have_any_common_ancestor(descendant, column)
    assert column.GetNumStrataDeposited() == 128
