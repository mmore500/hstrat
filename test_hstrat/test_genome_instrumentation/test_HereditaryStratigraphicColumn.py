from copy import deepcopy
import itertools as it
import random

import pytest

from hstrat import hstrat


@pytest.mark.parametrize(
    "retention_policy",
    [
        hstrat.perfect_resolution_algo.Policy(),
        hstrat.nominal_resolution_algo.Policy(),
        hstrat.fixed_resolution_algo.Policy(fixed_resolution=10),
    ],
)
@pytest.mark.parametrize(
    "ordered_store",
    [
        hstrat.HereditaryStratumOrderedStoreDict,
        hstrat.HereditaryStratumOrderedStoreList,
        hstrat.HereditaryStratumOrderedStoreTree,
    ],
)
def test_Clone1(retention_policy, ordered_store):
    original1 = hstrat.HereditaryStratigraphicColumn(
        stratum_ordered_store_factory=ordered_store,
        stratum_retention_policy=retention_policy,
    )
    original1_copy1 = deepcopy(original1)
    original1_copy2 = original1.Clone()

    assert original1 == original1_copy1
    assert original1 == original1_copy2
    assert original1_copy1 == original1_copy2

    for first in original1, original1_copy1, original1_copy2:
        for second in original1, original1_copy1, original1_copy2:
            assert first.HasAnyCommonAncestorWith(second)


@pytest.mark.parametrize(
    "retention_policy",
    [
        hstrat.perfect_resolution_algo.Policy(),
        hstrat.nominal_resolution_algo.Policy(),
        hstrat.fixed_resolution_algo.Policy(fixed_resolution=10),
    ],
)
@pytest.mark.parametrize(
    "ordered_store",
    [
        hstrat.HereditaryStratumOrderedStoreDict,
        hstrat.HereditaryStratumOrderedStoreList,
        hstrat.HereditaryStratumOrderedStoreTree,
    ],
)
def test_Clone2(retention_policy, ordered_store):
    original2 = hstrat.HereditaryStratigraphicColumn(
        stratum_ordered_store_factory=ordered_store,
        stratum_retention_policy=retention_policy,
    )
    original2.DepositStratum()
    original2.DepositStratum()

    original2_copy1 = deepcopy(original2)
    original2_copy2 = original2.Clone()

    for which in original2, original2_copy1, original2_copy2:
        for __ in range(20):
            which.DepositStratum()

    for first in original2, original2_copy1, original2_copy2:
        for second in original2, original2_copy1, original2_copy2:
            assert first.HasAnyCommonAncestorWith(second)


@pytest.mark.parametrize(
    "retention_policy",
    [
        hstrat.perfect_resolution_algo.Policy(),
        hstrat.nominal_resolution_algo.Policy(),
        hstrat.fixed_resolution_algo.Policy(fixed_resolution=10),
    ],
)
@pytest.mark.parametrize(
    "ordered_store",
    [
        hstrat.HereditaryStratumOrderedStoreDict,
        hstrat.HereditaryStratumOrderedStoreList,
        hstrat.HereditaryStratumOrderedStoreTree,
    ],
)
def test_Clone3(retention_policy, ordered_store):
    column = hstrat.HereditaryStratigraphicColumn(
        initial_stratum_annotation=0,
        stratum_ordered_store_factory=ordered_store,
        stratum_retention_policy=hstrat.perfect_resolution_algo.Policy(),
    )
    population = [column.Clone() for __ in range(3)]

    for generation in range(100):

        for f, s in it.combinations(population, 2):
            assert not f.HasDiscardedStrata()
            assert not s.HasDiscardedStrata()
            assert f.HasAnyCommonAncestorWith(s)
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
    "retention_policy",
    [
        hstrat.perfect_resolution_algo.Policy(),
        hstrat.nominal_resolution_algo.Policy(),
        hstrat.fixed_resolution_algo.Policy(fixed_resolution=10),
    ],
)
@pytest.mark.parametrize(
    "ordered_store",
    [
        hstrat.HereditaryStratumOrderedStoreDict,
        hstrat.HereditaryStratumOrderedStoreList,
        hstrat.HereditaryStratumOrderedStoreTree,
    ],
)
def test_Clone4(retention_policy, ordered_store):
    # regression test for bug with tree store cloning
    column = hstrat.HereditaryStratigraphicColumn(
        initial_stratum_annotation=0,
        stratum_ordered_store_factory=ordered_store,
        stratum_retention_policy=hstrat.perfect_resolution_algo.Policy(),
    )
    population = [column.Clone() for __ in range(3)]

    for generation in range(100):

        for f, s in it.combinations(population, 2):
            assert not f.HasDiscardedStrata()
            assert f.HasAnyCommonAncestorWith(s)
            assert hstrat.get_last_common_stratum_between(f, s) is not None

        # advance generation
        population[0] = population[0].Clone()
        for individual in population:
            if random.choice([True, False]):
                individual.DepositStratum()


@pytest.mark.parametrize(
    "retention_policy",
    [
        hstrat.perfect_resolution_algo.Policy(),
        hstrat.nominal_resolution_algo.Policy(),
        hstrat.fixed_resolution_algo.Policy(fixed_resolution=10),
    ],
)
@pytest.mark.parametrize(
    "ordered_store",
    [
        hstrat.HereditaryStratumOrderedStoreDict,
        hstrat.HereditaryStratumOrderedStoreList,
        hstrat.HereditaryStratumOrderedStoreTree,
    ],
)
def test_eq(
    retention_policy,
    ordered_store,
):

    original1 = hstrat.HereditaryStratigraphicColumn(
        stratum_ordered_store_factory=ordered_store,
        stratum_retention_policy=retention_policy,
    )
    copy1 = deepcopy(original1)
    copy2 = original1.Clone()
    original2 = hstrat.HereditaryStratigraphicColumn(
        stratum_ordered_store_factory=ordered_store,
        stratum_retention_policy=retention_policy,
    )

    assert original1 == copy1
    assert original1 == copy2
    assert copy1 == copy2
    assert original1 != original2
    assert copy1 != original2
    assert copy2 != original2

    copy1.DepositStratum()
    assert original1 != copy1

    original1.DepositStratum()
    assert original1 != copy1


@pytest.mark.parametrize(
    "retention_policy",
    [
        hstrat.perfect_resolution_algo.Policy(),
        hstrat.nominal_resolution_algo.Policy(),
        hstrat.fixed_resolution_algo.Policy(fixed_resolution=10),
    ],
)
@pytest.mark.parametrize(
    "ordered_store",
    [
        hstrat.HereditaryStratumOrderedStoreDict,
        hstrat.HereditaryStratumOrderedStoreList,
        pytest.param(
            hstrat.HereditaryStratumOrderedStoreTree,
            marks=pytest.mark.heavy,
        ),
    ],
)
def test_annotation(retention_policy, ordered_store):
    column = hstrat.HereditaryStratigraphicColumn(
        initial_stratum_annotation=0,
        stratum_ordered_store_factory=ordered_store,
        stratum_retention_policy=retention_policy,
    )
    population = [column.Clone() for __ in range(10)]

    for generation in range(100):
        for f, s in it.combinations(population, 2):
            lb, ub = f.CalcRankOfMrcaBoundsWith(s)
            assert (
                lb
                <= hstrat.get_last_common_stratum_between(f, s).GetAnnotation()
                < ub
            )
            assert (
                lb
                <= hstrat.get_last_common_stratum_between(s, f).GetAnnotation()
                < ub
            )

        # advance generation
        random.shuffle(population)
        for target in range(5):
            population[target] = population[-1].Clone()
        for individual in population:
            individual.DepositStratum(
                annotation=generation + 1,
            )


@pytest.mark.parametrize(
    "retention_policy",
    [
        hstrat.perfect_resolution_algo.Policy(),
        hstrat.nominal_resolution_algo.Policy(),
        hstrat.fixed_resolution_algo.Policy(fixed_resolution=10),
    ],
)
@pytest.mark.parametrize(
    "ordered_store",
    [
        hstrat.HereditaryStratumOrderedStoreDict,
        hstrat.HereditaryStratumOrderedStoreList,
        hstrat.HereditaryStratumOrderedStoreTree,
    ],
)
def test_always_store_rank_in_stratum(retention_policy, ordered_store):
    first = hstrat.HereditaryStratigraphicColumn(
        always_store_rank_in_stratum=True,
        stratum_ordered_store_factory=ordered_store,
        stratum_retention_policy=retention_policy,
    )
    second = hstrat.HereditaryStratigraphicColumn(
        always_store_rank_in_stratum=False,
        stratum_ordered_store_factory=ordered_store,
        stratum_retention_policy=retention_policy,
    )

    assert not first._ShouldOmitStratumDepositionRank()
    assert first.GetStratumAtColumnIndex(0).GetDepositionRank() == 0
    if retention_policy.CalcRankAtColumnIndex is not None:
        assert second._ShouldOmitStratumDepositionRank()
        assert second.GetStratumAtColumnIndex(0).GetDepositionRank() is None
    else:
        assert not second._ShouldOmitStratumDepositionRank()
        assert second.GetStratumAtColumnIndex(0).GetDepositionRank() == 0

    for gen in range(100):
        assert first.DiffRetainedRanks(second) == (set(), set())
        first.DepositStratum()
        second.DepositStratum()


def test_GetNumStrataDeposited():
    column = hstrat.HereditaryStratigraphicColumn()
    for i in range(10):
        assert column.GetNumStrataDeposited() == i + 1
        column.DepositStratum()


def test_CloneDescendant():
    column = hstrat.HereditaryStratigraphicColumn()
    assert column.GetNumStrataDeposited() == 1
    descendant = column.CloneDescendant(stratum_annotation="annotation")
    assert descendant.GetNumStrataDeposited() == 2
    assert descendant.HasAnyCommonAncestorWith(column)
    assert column.GetNumStrataDeposited() == 1
    assert (
        descendant.GetStratumAtColumnIndex(
            descendant.GetNumStrataRetained() - 1
        ).GetAnnotation()
        == "annotation"
    )


def test_maximal_retention_policy():
    first = hstrat.HereditaryStratigraphicColumn(
        stratum_retention_policy=hstrat.perfect_resolution_algo.Policy(),
    )
    second = first.Clone()
    third = first.Clone()

    for gen in range(100):
        assert first.GetNumStrataRetained() == gen + 1
        assert second.GetNumStrataRetained() == gen + 1
        assert third.GetNumStrataRetained() == 1

        assert first.CalcRankOfMrcaUncertaintyWith(second) == 0
        assert first.CalcRankOfMrcaUncertaintyWith(third) == 0

        assert first.CalcRanksSinceMrcaUncertaintyWith(second) == 0
        assert second.CalcRanksSinceMrcaUncertaintyWith(first) == 0
        assert first.CalcRanksSinceMrcaUncertaintyWith(third) == 0
        assert third.CalcRanksSinceMrcaUncertaintyWith(first) == 0

        first.DepositStratum()
        second.DepositStratum()
        # no layers deposited onto third


def test_minimal_retention_policy():
    first = hstrat.HereditaryStratigraphicColumn(
        stratum_retention_policy=hstrat.nominal_resolution_algo.Policy(),
    )
    second = first.Clone()
    third = first.Clone()

    for gen in range(100):
        assert first.GetNumStrataRetained() == min(2, gen + 1)
        assert second.GetNumStrataRetained() == min(2, gen + 1)
        assert third.GetNumStrataRetained() == 1

        assert first.CalcRankOfMrcaUncertaintyWith(second) == max(0, gen - 1)
        assert first.CalcRankOfMrcaUncertaintyWith(third) == 0

        assert first.CalcRanksSinceMrcaUncertaintyWith(second) == max(
            0, gen - 1
        )
        assert second.CalcRanksSinceMrcaUncertaintyWith(first) == max(
            0, gen - 1
        )
        assert first.CalcRanksSinceMrcaUncertaintyWith(third) == 0
        assert third.CalcRanksSinceMrcaUncertaintyWith(first) == 0

        first.DepositStratum()
        second.DepositStratum()
        # no layers deposited onto third


def test_CalcProbabilityDifferentiaCollision():
    assert (
        hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=1,
        ).CalcProbabilityDifferentiaCollision()
        == 0.5
    )
    assert (
        hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=2,
        ).CalcProbabilityDifferentiaCollision()
        == 0.25
    )
    assert (
        hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=3,
        ).CalcProbabilityDifferentiaCollision()
        == 0.125
    )
    assert (
        hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=8,
        ).CalcProbabilityDifferentiaCollision()
        == 1.0 / 256.0
    )


def test_CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions():
    assert (
        hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=1,
        ).CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
            significance_level=1.0 - 0.49
        )
        == 1
    )
    assert (
        hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=1,
        ).CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
            significance_level=1.0 - 0.95
        )
        == 5
    )
    assert (
        hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=2,
        ).CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
            significance_level=1.0 - 0.95
        )
        == 3
    )
    assert (
        hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=5,
        ).CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
            significance_level=1.0 - 0.95
        )
        == 1
    )
    assert (
        hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=64,
        ).CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
            significance_level=1.0 - 0.49
        )
        == 1
    )
    assert (
        hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=64,
        ).CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
            significance_level=1.0 - 0.95
        )
        == 1
    )
    assert (
        hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=64,
        ).CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
            significance_level=1.0 - 0.99
        )
        == 1
    )


def test_CalcRankOfMrcaBoundsWithProvidedConfidenceLevel():
    c1 = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=1,
    )
    assert c1.CalcRankOfMrcaBoundsWithProvidedConfidenceLevel(0.5) == 0.5
    assert c1.CalcRankOfMrcaBoundsWithProvidedConfidenceLevel(0.6) == 0.75
    assert c1.CalcRankOfMrcaBoundsWithProvidedConfidenceLevel(0.75) == 0.75

    c2 = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=64,
    )
    p = 1 / 2**64
    assert c2.CalcRankOfMrcaBoundsWithProvidedConfidenceLevel(0.5) == 1 - p
    assert c2.CalcRankOfMrcaBoundsWithProvidedConfidenceLevel(0.6) == 1 - p
    assert c2.CalcRankOfMrcaBoundsWithProvidedConfidenceLevel(0.75) == 1 - p
    assert c2.CalcRankOfMrcaBoundsWithProvidedConfidenceLevel(0.95) == 1 - p
    assert c2.CalcRankOfMrcaBoundsWithProvidedConfidenceLevel(0.99) == 1 - p


def test_CalcRanksSinceMrcaBoundsWithProvidedConfidenceLevel():
    c1 = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=1,
    )
    assert c1.CalcRanksSinceMrcaBoundsWithProvidedConfidenceLevel(0.5) == 0.5
    assert c1.CalcRanksSinceMrcaBoundsWithProvidedConfidenceLevel(0.6) == 0.75
    assert c1.CalcRanksSinceMrcaBoundsWithProvidedConfidenceLevel(0.75) == 0.75

    c2 = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=64,
    )
    p = 1 / 2**64
    assert c2.CalcRanksSinceMrcaBoundsWithProvidedConfidenceLevel(0.5) == 1 - p
    assert c2.CalcRanksSinceMrcaBoundsWithProvidedConfidenceLevel(0.6) == 1 - p
    assert (
        c2.CalcRanksSinceMrcaBoundsWithProvidedConfidenceLevel(0.75) == 1 - p
    )
    assert (
        c2.CalcRanksSinceMrcaBoundsWithProvidedConfidenceLevel(0.95) == 1 - p
    )
    assert (
        c2.CalcRanksSinceMrcaBoundsWithProvidedConfidenceLevel(0.99) == 1 - p
    )
