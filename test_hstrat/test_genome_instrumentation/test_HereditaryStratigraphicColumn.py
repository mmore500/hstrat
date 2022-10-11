from copy import deepcopy
import itertools as it
import pickle
import random
import tempfile

import pytest

from hstrat import hstrat
from hstrat import genome_instrumentation


@pytest.mark.parametrize(
    "impl",
    genome_instrumentation._HereditaryStratigraphicColumn_.impls,
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
def test_Clone1(impl, retention_policy, ordered_store):
    original1 = impl(
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
            assert hstrat.does_have_any_common_ancestor(first, second)


@pytest.mark.parametrize(
    "impl",
    genome_instrumentation._HereditaryStratigraphicColumn_.impls,
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
def test_Clone2(impl, retention_policy, ordered_store):
    original2 = impl(
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
            assert hstrat.does_have_any_common_ancestor(first, second)


@pytest.mark.parametrize(
    "impl",
    genome_instrumentation._HereditaryStratigraphicColumn_.impls,
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
def test_Clone3(impl, retention_policy, ordered_store):
    column = impl(
        initial_stratum_annotation=0,
        stratum_ordered_store_factory=ordered_store,
        stratum_retention_policy=hstrat.perfect_resolution_algo.Policy(),
    )
    population = [column.Clone() for __ in range(3)]

    for generation in range(100):

        for f, s in it.combinations(population, 2):
            assert not f.HasDiscardedStrata()
            assert not s.HasDiscardedStrata()
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
    "impl",
    genome_instrumentation._HereditaryStratigraphicColumn_.impls,
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
def test_Clone4(impl, retention_policy, ordered_store):
    # regression test for bug with tree store cloning
    column = impl(
        initial_stratum_annotation=0,
        stratum_ordered_store_factory=ordered_store,
        stratum_retention_policy=hstrat.perfect_resolution_algo.Policy(),
    )
    population = [column.Clone() for __ in range(3)]

    for generation in range(100):

        for f, s in it.combinations(population, 2):
            assert not f.HasDiscardedStrata()
            assert hstrat.does_have_any_common_ancestor(f, s)
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
def test_pickle(retention_policy, ordered_store):
    original = hstrat.HereditaryStratigraphicColumn(
        stratum_ordered_store_factory=ordered_store,
        stratum_retention_policy=retention_policy,
    )
    with tempfile.TemporaryDirectory() as tmp_path:
        with open(f"{tmp_path}/data", "wb") as tmp_file:
            pickle.dump(original, tmp_file)

        with open(f"{tmp_path}/data", "rb") as tmp_file:
            reconstituted = pickle.load(tmp_file)
            assert reconstituted == original


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
def test_pickle_with_deposits(retention_policy, ordered_store):
    original = hstrat.HereditaryStratigraphicColumn(
        stratum_ordered_store_factory=ordered_store,
        stratum_retention_policy=retention_policy,
    )
    for __ in range(100):
        original.DepositStratum()
    with tempfile.TemporaryDirectory() as tmp_path:
        with open(f"{tmp_path}/data", "wb") as tmp_file:
            pickle.dump(original, tmp_file)

        with open(f"{tmp_path}/data", "rb") as tmp_file:
            reconstituted = pickle.load(tmp_file)
            assert reconstituted == original


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
def test_pickle_with_population(retention_policy, ordered_store):
    population = [
        hstrat.HereditaryStratigraphicColumn(
            stratum_ordered_store_factory=ordered_store,
            stratum_retention_policy=retention_policy,
        )
        for idx in range(20)
    ]

    for gen in range(10**3):
        population[random.randrange(len(population))] = population[
            random.randrange(len(population))
        ].CloneDescendant()

    for original in population:
        with tempfile.TemporaryDirectory() as tmp_path:
            with open(f"{tmp_path}/data", "wb") as tmp_file:
                pickle.dump(original, tmp_file)

            with open(f"{tmp_path}/data", "rb") as tmp_file:
                reconstituted = pickle.load(tmp_file)
                assert reconstituted == original


@pytest.mark.parametrize(
    "impl",
    genome_instrumentation._HereditaryStratigraphicColumn_.impls,
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
def test_eq(
    impl,
    retention_policy,
    ordered_store,
):

    original1 = impl(
        stratum_ordered_store_factory=ordered_store,
        stratum_retention_policy=retention_policy,
    )
    copy1 = deepcopy(original1)
    copy2 = original1.Clone()
    original2 = impl(
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
    "impl",
    genome_instrumentation._HereditaryStratigraphicColumn_.impls,
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
        pytest.param(
            hstrat.HereditaryStratumOrderedStoreTree,
            marks=pytest.mark.heavy,
        ),
    ],
)
def test_annotation(impl, retention_policy, ordered_store):
    column = impl(
        initial_stratum_annotation=0,
        stratum_ordered_store_factory=ordered_store,
        stratum_retention_policy=retention_policy,
    )
    population = [column.Clone() for __ in range(10)]

    for generation in range(100):
        for f, s in it.combinations(population, 2):
            lb, ub = hstrat.calc_rank_of_mrca_bounds_between(f, s)
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
    "impl",
    genome_instrumentation._HereditaryStratigraphicColumn_.impls,
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
def test_always_store_rank_in_stratum(impl, retention_policy, ordered_store):
    first = impl(
        always_store_rank_in_stratum=True,
        stratum_ordered_store_factory=ordered_store,
        stratum_retention_policy=retention_policy,
    )
    second = impl(
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
        assert hstrat.diff_retained_ranks(first, second) == (set(), set())
        first.DepositStratum()
        second.DepositStratum()


@pytest.mark.parametrize(
    "impl",
    genome_instrumentation._HereditaryStratigraphicColumn_.impls,
)
def test_GetNumStrataDeposited(impl):
    column = impl()
    for i in range(10):
        assert column.GetNumStrataDeposited() == i + 1
        column.DepositStratum()


@pytest.mark.parametrize(
    "impl",
    genome_instrumentation._HereditaryStratigraphicColumn_.impls,
)
def test_CloneDescendant(impl):
    column = impl()
    assert column.GetNumStrataDeposited() == 1
    descendant = column.CloneDescendant(stratum_annotation="annotation")
    assert descendant.GetNumStrataDeposited() == 2
    assert hstrat.does_have_any_common_ancestor(descendant, column)
    assert column.GetNumStrataDeposited() == 1
    assert (
        descendant.GetStratumAtColumnIndex(
            descendant.GetNumStrataRetained() - 1
        ).GetAnnotation()
        == "annotation"
    )


@pytest.mark.parametrize(
    "impl",
    genome_instrumentation._HereditaryStratigraphicColumn_.impls,
)
def test_maximal_retention_policy(impl):
    first = impl(
        stratum_retention_policy=hstrat.perfect_resolution_algo.Policy(),
    )
    second = first.Clone()
    third = first.Clone()

    for gen in range(100):
        assert first.GetNumStrataRetained() == gen + 1
        assert second.GetNumStrataRetained() == gen + 1
        assert third.GetNumStrataRetained() == 1

        assert hstrat.calc_rank_of_mrca_uncertainty_between(first, second) == 0
        assert hstrat.calc_rank_of_mrca_uncertainty_between(first, third) == 0

        assert (
            hstrat.calc_ranks_since_mrca_uncertainty_with(first, second) == 0
        )
        assert (
            hstrat.calc_ranks_since_mrca_uncertainty_with(second, first) == 0
        )
        assert hstrat.calc_ranks_since_mrca_uncertainty_with(first, third) == 0
        assert hstrat.calc_ranks_since_mrca_uncertainty_with(third, first) == 0

        first.DepositStratum()
        second.DepositStratum()
        # no layers deposited onto third


@pytest.mark.parametrize(
    "impl",
    genome_instrumentation._HereditaryStratigraphicColumn_.impls,
)
def test_minimal_retention_policy(impl):
    first = impl(
        stratum_retention_policy=hstrat.nominal_resolution_algo.Policy(),
    )
    second = first.Clone()
    third = first.Clone()

    for gen in range(100):
        assert first.GetNumStrataRetained() == min(2, gen + 1)
        assert second.GetNumStrataRetained() == min(2, gen + 1)
        assert third.GetNumStrataRetained() == 1

        assert hstrat.calc_rank_of_mrca_uncertainty_between(
            first, second
        ) == max(0, gen - 1)
        assert hstrat.calc_rank_of_mrca_uncertainty_between(first, third) == 0

        assert hstrat.calc_ranks_since_mrca_uncertainty_with(
            first, second
        ) == max(0, gen - 1)
        assert hstrat.calc_ranks_since_mrca_uncertainty_with(
            second, first
        ) == max(0, gen - 1)
        assert hstrat.calc_ranks_since_mrca_uncertainty_with(first, third) == 0
        assert hstrat.calc_ranks_since_mrca_uncertainty_with(third, first) == 0

        first.DepositStratum()
        second.DepositStratum()
        # no layers deposited onto third


@pytest.mark.parametrize(
    "impl",
    genome_instrumentation._HereditaryStratigraphicColumn_.impls,
)
def test_CalcProbabilityDifferentiaCollision(impl):
    assert (
        impl(
            stratum_differentia_bit_width=1,
        ).CalcProbabilityDifferentiaCollision()
        == 0.5
    )
    try:
        assert (
            impl(
                stratum_differentia_bit_width=2,
            ).CalcProbabilityDifferentiaCollision()
            == 0.25
        )
    except ValueError:
        pass
    try:
        assert (
            impl(
                stratum_differentia_bit_width=3,
            ).CalcProbabilityDifferentiaCollision()
            == 0.125
        )
    except ValueError:
        pass
    assert (
        impl(
            stratum_differentia_bit_width=8,
        ).CalcProbabilityDifferentiaCollision()
        == 1.0 / 256.0
    )


@pytest.mark.parametrize(
    "impl",
    genome_instrumentation._HereditaryStratigraphicColumn_.impls,
)
def test_CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(impl):
    assert (
        impl(
            stratum_differentia_bit_width=1,
        ).CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
            significance_level=1.0 - 0.49
        )
        == 1
    )
    assert (
        impl(
            stratum_differentia_bit_width=1,
        ).CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
            significance_level=1.0 - 0.95
        )
        == 5
    )
    try:
        assert (
            impl(
                stratum_differentia_bit_width=2,
            ).CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
                significance_level=1.0 - 0.95
            )
            == 3
        )
    except ValueError:
        pass
    try:
        assert (
            impl(
                stratum_differentia_bit_width=5,
            ).CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
                significance_level=1.0 - 0.95
            )
            == 1
        )
    except ValueError:
        pass
    assert (
        impl(
            stratum_differentia_bit_width=64,
        ).CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
            significance_level=1.0 - 0.49
        )
        == 1
    )
    assert (
        impl(
            stratum_differentia_bit_width=64,
        ).CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
            significance_level=1.0 - 0.95
        )
        == 1
    )
    assert (
        impl(
            stratum_differentia_bit_width=64,
        ).CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
            significance_level=1.0 - 0.99
        )
        == 1
    )
