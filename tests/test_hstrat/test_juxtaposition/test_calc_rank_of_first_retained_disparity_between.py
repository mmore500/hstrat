import itertools as it
import random

from iterify import iterify
import opytional as opyt
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
        pytest.param(
            hstrat.HereditaryStratumOrderedStoreTree,
            marks=pytest.mark.heavy,
        ),
    ],
)
def test_comparison_commutativity_asyncrhonous(
    retention_policy,
    ordered_store,
):
    population = [
        hstrat.HereditaryStratigraphicColumn(
            stratum_ordered_store_factory=ordered_store,
            stratum_retention_policy=retention_policy,
        )
        for __ in range(10)
    ]

    for generation in range(100):
        for first, second in it.combinations(population, 2):
            # assert commutativity
            assert hstrat.calc_rank_of_first_retained_disparity_between(
                first,
                second,
            ) == hstrat.calc_rank_of_first_retained_disparity_between(
                second,
                first,
            )

        # advance generation
        random.shuffle(population)
        for target in range(5):
            population[target] = population[-1].CloneDescendant()
        for individual in population:
            # asynchronous generations
            if random.choice([True, False]):
                individual.DepositStratum()


@pytest.mark.parametrize(
    "retention_policy",
    [
        pytest.param(
            hstrat.perfect_resolution_algo.Policy(),
            marks=pytest.mark.heavy_2a,
        ),
        hstrat.nominal_resolution_algo.Policy(),
        hstrat.fixed_resolution_algo.Policy(fixed_resolution=10),
    ],
)
@pytest.mark.parametrize(
    "ordered_store",
    [
        pytest.param(
            hstrat.HereditaryStratumOrderedStoreDict,
            marks=pytest.mark.heavy_2b,
        ),
        hstrat.HereditaryStratumOrderedStoreList,
        pytest.param(
            hstrat.HereditaryStratumOrderedStoreTree,
            marks=pytest.mark.heavy,
        ),
    ],
)
def test_comparison_commutativity_syncrhonous(
    retention_policy,
    ordered_store,
):

    population = [
        hstrat.HereditaryStratigraphicColumn(
            stratum_ordered_store_factory=ordered_store,
            stratum_retention_policy=retention_policy,
        )
        for __ in range(10)
    ]

    for generation in range(100):

        for first, second in it.combinations(population, 2):
            # assert commutativity
            assert hstrat.calc_rank_of_first_retained_disparity_between(
                first,
                second,
            ) == hstrat.calc_rank_of_first_retained_disparity_between(
                second,
                first,
            )

        # advance generation
        random.shuffle(population)
        for target in range(5):
            population[target] = population[-1].Clone()
        # synchronous generations
        for individual in population:
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
        pytest.param(
            hstrat.HereditaryStratumOrderedStoreTree,
            marks=pytest.mark.heavy,
        ),
    ],
)
def test_comparison_validity(retention_policy, ordered_store):
    population = [
        hstrat.HereditaryStratigraphicColumn(
            stratum_ordered_store_factory=ordered_store,
            stratum_retention_policy=retention_policy,
        )
        for __ in range(10)
    ]

    for generation in range(100):
        for first, second in it.combinations(population, 2):
            lcrw = hstrat.calc_rank_of_last_retained_commonality_between(
                first, second
            )
            if lcrw is not None:
                assert 0 <= lcrw <= generation

            fdrw = hstrat.calc_rank_of_first_retained_disparity_between(
                first,
                second,
            )
            if fdrw is not None:
                assert 0 <= fdrw <= generation

            assert hstrat.calc_rank_of_mrca_bounds_between(first, second) in [
                (lcrw, opyt.or_value(fdrw, first.GetNumStrataDeposited())),
                None,
            ]
            if lcrw is not None and fdrw is not None:
                assert lcrw < fdrw

        # advance generations asynchronously
        random.shuffle(population)
        for target in range(5):
            population[target] = population[-1].Clone()
        for individual in population:
            if random.choice([True, False]):
                individual.DepositStratum()


@pytest.mark.parametrize(
    "retention_policy1",
    [
        hstrat.perfect_resolution_algo.Policy(),
        hstrat.nominal_resolution_algo.Policy(),
        hstrat.fixed_resolution_algo.Policy(fixed_resolution=10),
    ],
)
@pytest.mark.parametrize(
    "retention_policy2",
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
def test_scenario_no_mrca(
    retention_policy1,
    retention_policy2,
    ordered_store,
):
    first = hstrat.HereditaryStratigraphicColumn(
        stratum_ordered_store_factory=ordered_store,
        stratum_retention_policy=retention_policy1,
    )
    second = hstrat.HereditaryStratigraphicColumn(
        stratum_ordered_store_factory=ordered_store,
        stratum_retention_policy=retention_policy2,
    )

    for generation in range(100):
        assert (
            hstrat.calc_rank_of_first_retained_disparity_between(first, second)
            == 0
        )
        assert (
            hstrat.calc_rank_of_first_retained_disparity_between(first, second)
            == 0
        )

        first.DepositStratum()
        second.DepositStratum()


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
def test_scenario_no_divergence(retention_policy, ordered_store):
    column = hstrat.HereditaryStratigraphicColumn(
        stratum_ordered_store_factory=ordered_store,
        stratum_retention_policy=retention_policy,
    )

    for generation in range(100):
        assert (
            hstrat.calc_rank_of_first_retained_disparity_between(
                column, column
            )
            is None
        )

        column.DepositStratum()


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
def test_scenario_partial_even_divergence(retention_policy, ordered_store):
    first = hstrat.HereditaryStratigraphicColumn(
        stratum_ordered_store_factory=ordered_store,
        stratum_retention_policy=retention_policy,
    )

    for generation in range(100):
        first.DepositStratum()

    second = first.Clone()

    first.DepositStratum()
    second.DepositStratum()

    for generation in range(101, 200):
        assert (
            100
            <= hstrat.calc_rank_of_first_retained_disparity_between(
                first, second
            )
            <= generation
        )

        first.DepositStratum()
        second.DepositStratum()


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
def test_scenario_partial_uneven_divergence(retention_policy, ordered_store):
    first = hstrat.HereditaryStratigraphicColumn(
        stratum_ordered_store_factory=ordered_store,
        stratum_retention_policy=retention_policy,
    )

    for generation in range(100):
        first.DepositStratum()

    second = first.Clone()

    first.DepositStratum()

    for generation in range(101, 200):
        assert (
            100
            <= hstrat.calc_rank_of_first_retained_disparity_between(
                first, second
            )
            <= generation
        )
        first.DepositStratum()

    second.DepositStratum()

    for generation in range(101, 200):
        assert (
            100
            <= hstrat.calc_rank_of_first_retained_disparity_between(
                first, second
            )
            <= generation + 1
        )
        second.DepositStratum()


@pytest.mark.parametrize(
    "ordered_store",
    [
        hstrat.HereditaryStratumOrderedStoreDict,
        hstrat.HereditaryStratumOrderedStoreList,
        hstrat.HereditaryStratumOrderedStoreTree,
    ],
)
@pytest.mark.parametrize(
    "differentia_width",
    [1, 2, 8],
)
def test_CalcRankOfFirstRetainedDisparityWith1(
    ordered_store,
    differentia_width,
):
    column = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=differentia_width,
        stratum_ordered_store_factory=ordered_store,
    )

    for generation in range(100):
        column.DepositStratum()

    offspring1 = column.CloneDescendant()
    offspring2 = column.CloneDescendant()

    if differentia_width == 64:
        for c1, c2 in it.combinations([column, offspring1, offspring2], 2):
            assert (
                hstrat.calc_rank_of_first_retained_disparity_between(
                    c2,
                    c2,
                )
                == column.GetNumStrataDeposited()
            )
            assert (
                hstrat.calc_rank_of_first_retained_disparity_between(
                    c2,
                    c1,
                )
                == column.GetNumStrataDeposited()
            )

    elif differentia_width == 1:
        assert (
            hstrat.calc_rank_of_first_retained_disparity_between(
                offspring1,
                offspring2,
            )
            < offspring2.GetNumStrataDeposited() - 1
        )
        assert (
            hstrat.calc_rank_of_first_retained_disparity_between(
                offspring2,
                offspring1,
            )
            < offspring2.GetNumStrataDeposited() - 1
        )
        for c in [offspring1, offspring2]:
            assert (
                hstrat.calc_rank_of_first_retained_disparity_between(
                    c,
                    column,
                )
                < column.GetNumStrataDeposited()
            )
            assert (
                hstrat.calc_rank_of_first_retained_disparity_between(
                    column,
                    c,
                )
                < column.GetNumStrataDeposited()
            )

    for c in [column, offspring1, offspring2]:
        if (
            c.CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
                significance_level=0.2,
            )
            > 1
        ):
            assert (
                hstrat.calc_rank_of_first_retained_disparity_between(
                    c,
                    c,
                    0.8,
                )
                == c.GetNumStrataDeposited()
                - c.CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
                    significance_level=0.2,
                )
                + 1
            )
        else:
            assert (
                hstrat.calc_rank_of_first_retained_disparity_between(
                    c,
                    c,
                    0.8,
                )
                is None
            )
        if (
            c.CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
                significance_level=0.05,
            )
            > 1
        ):
            assert (
                hstrat.calc_rank_of_first_retained_disparity_between(
                    c,
                    c,
                    0.95,
                )
                == c.GetNumStrataDeposited()
                - c.CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
                    significance_level=0.05,
                )
                + 1
            )
        else:
            assert (
                hstrat.calc_rank_of_first_retained_disparity_between(
                    c,
                    c,
                    0.95,
                )
                is None
            )

    for generation in range(100):
        offspring1.DepositStratum()
        offspring2.DepositStratum()

    for c1, c2 in it.combinations([column, offspring1, offspring2], 2):
        if differentia_width == 64:
            assert (
                hstrat.calc_rank_of_first_retained_disparity_between(
                    c1,
                    c2,
                )
                == column.GetNumStrataDeposited()
            )
            assert (
                hstrat.calc_rank_of_first_retained_disparity_between(
                    c2,
                    c1,
                )
                == column.GetNumStrataDeposited()
            )
        elif differentia_width == 1:
            assert hstrat.calc_rank_of_first_retained_disparity_between(
                c1, c2, 0.999999
            ) < hstrat.calc_rank_of_first_retained_disparity_between(
                c2, c1, 0.8
            )

    for c in [column, offspring1, offspring2]:
        if (
            c.CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
                significance_level=0.2,
            )
            > 1
        ):
            assert (
                hstrat.calc_rank_of_first_retained_disparity_between(c, c, 0.8)
                == c.GetNumStrataDeposited()
                - c.CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
                    significance_level=0.2,
                )
                + 1
            )
        else:
            assert (
                hstrat.calc_rank_of_first_retained_disparity_between(c, c, 0.8)
                is None
            )
        if (
            c.CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
                significance_level=0.05,
            )
            > 1
        ):
            assert (
                hstrat.calc_rank_of_first_retained_disparity_between(
                    c, c, 0.95
                )
                == c.GetNumStrataDeposited()
                - c.CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
                    significance_level=0.05,
                )
                + 1
            )
        else:
            assert (
                hstrat.calc_rank_of_first_retained_disparity_between(
                    c, c, 0.95
                )
                is None
            )


@pytest.mark.parametrize(
    "ordered_store",
    [
        hstrat.HereditaryStratumOrderedStoreDict,
        hstrat.HereditaryStratumOrderedStoreList,
        hstrat.HereditaryStratumOrderedStoreTree,
    ],
)
def test_CalcRankOfFirstRetainedDisparityWith2(ordered_store):
    column = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=1,
    )

    while True:
        offspring1 = column.CloneDescendant()
        offspring2 = column.CloneDescendant()

        res = hstrat.calc_rank_of_first_retained_disparity_between(
            offspring1,
            offspring2,
        )
        assert res == 0
        assert res == hstrat.calc_rank_of_first_retained_disparity_between(
            offspring2,
            offspring1,
        )

        res = hstrat.calc_rank_of_first_retained_disparity_between(
            offspring1,
            offspring2,
            0.49,
        )
        assert res in (None, 1)
        assert res == hstrat.calc_rank_of_first_retained_disparity_between(
            offspring2,
            offspring1,
            0.49,
        )
        if res == 1:
            break

    while True:
        offspring1 = column.CloneDescendant()
        offspring2 = column.CloneDescendant()

        res = hstrat.calc_rank_of_first_retained_disparity_between(
            offspring1,
            offspring2,
        )
        assert res == 0
        assert res == hstrat.calc_rank_of_first_retained_disparity_between(
            offspring2,
            offspring1,
        )

        res = hstrat.calc_rank_of_first_retained_disparity_between(
            offspring1,
            offspring2,
            0.49,
        )
        assert res in (None, 1)
        assert res == hstrat.calc_rank_of_first_retained_disparity_between(
            offspring2,
            offspring1,
            0.49,
        )
        if res is None:
            break

    for rep in range(500):
        offspring1 = column.CloneDescendant()
        offspring2 = column.CloneDescendant()

        res = hstrat.calc_rank_of_first_retained_disparity_between(
            offspring1,
            offspring2,
            0.49,
        )
        assert res in (None, 1)
        assert res == hstrat.calc_rank_of_first_retained_disparity_between(
            offspring2,
            offspring1,
            0.49,
        )

        for gen in range(8):
            offspring1.DepositStratum()
            offspring2.DepositStratum()
            # should occur about 1 in 20 times
            assert (
                hstrat.calc_rank_of_first_retained_disparity_between(
                    offspring2,
                    offspring1,
                )
                is not None
            )
            assert (
                hstrat.calc_rank_of_first_retained_disparity_between(
                    offspring1,
                    offspring2,
                )
                is not None
            )

    column = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=1,
    )

    for __ in range(100):
        column.DepositStratum()

    for rep in range(5):
        offspring1 = column.CloneDescendant()
        offspring2 = column.CloneDescendant()

        divergence_rank = offspring1.GetNumStrataDeposited() - 1

        res = hstrat.calc_rank_of_first_retained_disparity_between(
            offspring1,
            offspring2,
        )
        assert res < divergence_rank
        assert res == hstrat.calc_rank_of_first_retained_disparity_between(
            offspring2,
            offspring1,
        )

        for gen in range(10):
            offspring1.DepositStratum()
            offspring2.DepositStratum()

        res = hstrat.calc_rank_of_first_retained_disparity_between(
            offspring1,
            offspring2,
        )
        assert res is not None
        assert res < offspring1.GetNumStrataDeposited() - 1
        assert res == hstrat.calc_rank_of_first_retained_disparity_between(
            offspring2,
            offspring1,
        )

        for gen in range(42):
            offspring1.DepositStratum()

        res = hstrat.calc_rank_of_first_retained_disparity_between(
            offspring1,
            offspring2,
        )
        assert res is not None
        assert res < offspring2.GetNumStrataDeposited()
        assert res == hstrat.calc_rank_of_first_retained_disparity_between(
            offspring2,
            offspring1,
        )


@pytest.mark.parametrize(
    "ordered_store",
    [
        hstrat.HereditaryStratumOrderedStoreDict,
        hstrat.HereditaryStratumOrderedStoreList,
        hstrat.HereditaryStratumOrderedStoreTree,
    ],
)
def test_CalcRankOfFirstRetainedDisparityWith3(ordered_store):
    column = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=64,
        stratum_retention_policy=hstrat.nominal_resolution_algo.Policy(),
    )

    for generation in range(100):
        column.DepositStratum()

    offspring1 = column.CloneDescendant()
    offspring2 = column.CloneDescendant()

    for generation in range(100):
        offspring1.DepositStratum()
        offspring2.DepositStratum()

    for c2 in [offspring1, offspring2]:
        assert (
            hstrat.calc_rank_of_first_retained_disparity_between(
                column,
                c2,
            )
            == column.GetNumStrataDeposited()
        )

        assert (
            hstrat.calc_rank_of_first_retained_disparity_between(
                c2,
                column,
            )
            == column.GetNumStrataDeposited()
        )

    assert (
        hstrat.calc_rank_of_first_retained_disparity_between(
            offspring1,
            offspring2,
        )
        == offspring1.GetNumStrataDeposited() - 1
    )
    assert (
        hstrat.calc_rank_of_first_retained_disparity_between(
            offspring2,
            offspring1,
        )
        == offspring1.GetNumStrataDeposited() - 1
    )


@pytest.mark.parametrize(
    "ordered_store",
    [
        hstrat.HereditaryStratumOrderedStoreDict,
        hstrat.HereditaryStratumOrderedStoreList,
        hstrat.HereditaryStratumOrderedStoreTree,
    ],
)
def test_CalcRankOfFirstRetainedDisparityWith4(ordered_store):
    column = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=1,
        stratum_retention_policy=hstrat.fixed_resolution_algo.Policy(2),
    )

    while True:
        offspring1 = column.CloneDescendant()
        offspring2 = column.CloneDescendant()

        res = hstrat.calc_rank_of_first_retained_disparity_between(
            offspring1,
            offspring2,
        )
        assert res == 0
        assert res == hstrat.calc_rank_of_first_retained_disparity_between(
            offspring2,
            offspring1,
        )

        for gen in range(20):
            offspring1.DepositStratum()

        assert (
            hstrat.calc_rank_of_first_retained_disparity_between(
                offspring2,
                offspring1,
            )
            is not None
        )

        for gen in range(20):
            offspring2.DepositStratum()

        assert (
            hstrat.calc_rank_of_first_retained_disparity_between(
                offspring2,
                offspring1,
            )
            is not None
        )
        break

    column = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=1,
        stratum_retention_policy=hstrat.fixed_resolution_algo.Policy(2),
    )

    for __ in range(100):
        column.DepositStratum()

    for rep in range(50):
        offspring1 = column.CloneDescendant()
        offspring2 = column.CloneDescendant()

        res = hstrat.calc_rank_of_first_retained_disparity_between(
            offspring1,
            offspring2,
        )

        idx = (
            offspring1.GetNumStrataRetained()
            - offspring1.CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
                significance_level=0.05
            )
            + 1
        )
        assert (
            offspring1.GetRankAtColumnIndex(idx - 1)
            <= res
            <= offspring1.GetRankAtColumnIndex(idx)
        )

        assert res == hstrat.calc_rank_of_first_retained_disparity_between(
            offspring2,
            offspring1,
        )

        for gen in range(10):
            offspring1.DepositStratum()
            offspring2.DepositStratum()

        res = hstrat.calc_rank_of_first_retained_disparity_between(
            offspring1,
            offspring2,
        )
        assert res is not None
        assert res == hstrat.calc_rank_of_first_retained_disparity_between(
            offspring2,
            offspring1,
        )

        for gen in range(42):
            offspring1.DepositStratum()

        res = hstrat.calc_rank_of_first_retained_disparity_between(
            offspring1,
            offspring2,
        )
        assert res is not None
        assert res == hstrat.calc_rank_of_first_retained_disparity_between(
            offspring2,
            offspring1,
        )


@pytest.mark.parametrize(
    "ordered_store",
    [
        hstrat.HereditaryStratumOrderedStoreDict,
        hstrat.HereditaryStratumOrderedStoreList,
        hstrat.HereditaryStratumOrderedStoreTree,
    ],
)
@pytest.mark.parametrize(
    "differentia_width",
    [1, 2, 8],
)
def test_CalcRankOfFirstRetainedDisparityWith5(
    ordered_store,
    differentia_width,
):
    column = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=differentia_width,
        stratum_ordered_store_factory=ordered_store,
        stratum_retention_policy=hstrat.fixed_resolution_algo.Policy(2),
    )

    for generation in range(100):
        column.DepositStratum()

    offspring1 = column.CloneDescendant()
    offspring2 = column.CloneDescendant()

    assert column.GetNumStrataDeposited() == 101
    assert offspring1.GetNumStrataDeposited() == 102
    assert offspring2.GetNumStrataDeposited() == 102

    for c1, c2 in it.combinations([column, offspring1, offspring2], 2):
        if differentia_width == 64:
            assert (
                hstrat.calc_rank_of_first_retained_disparity_between(
                    c1,
                    c2,
                )
                == column.GetNumStrataDeposited()
            )
            assert (
                hstrat.calc_rank_of_first_retained_disparity_between(
                    c2,
                    c1,
                )
                == column.GetNumStrataDeposited()
            )
        elif differentia_width == 1:
            assert (
                hstrat.calc_rank_of_first_retained_disparity_between(
                    c1,
                    c2,
                )
                < column.GetNumStrataDeposited()
            )
            assert (
                hstrat.calc_rank_of_first_retained_disparity_between(
                    c2,
                    c1,
                )
                < column.GetNumStrataDeposited()
            )

    for c in [column, offspring1, offspring2]:
        for conf in 0.8, 0.95, 0.99:
            col_idx = (
                c.GetNumStrataRetained()
                - c.CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
                    significance_level=1 - conf,
                )
                + 1
            )
            if col_idx == c.GetNumStrataRetained():
                assert (
                    c.CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
                        significance_level=1 - conf,
                    )
                    == 1
                )
                assert (
                    hstrat.calc_rank_of_first_retained_disparity_between(
                        c, c, conf
                    )
                    is None
                )
            else:
                assert hstrat.calc_rank_of_first_retained_disparity_between(
                    c, c, conf
                ) == c.GetRankAtColumnIndex(col_idx)

    for generation in range(99):
        offspring1.DepositStratum()
        offspring2.DepositStratum()

    for c1, c2 in it.combinations([column, offspring1, offspring2], 2):
        if differentia_width == 64:
            assert (
                hstrat.calc_rank_of_first_retained_disparity_between(
                    c1,
                    c2,
                )
                == column.GetNumStrataDeposited()
            )
            assert (
                hstrat.calc_rank_of_first_retained_disparity_between(
                    c2,
                    c1,
                )
                == column.GetNumStrataDeposited()
            )
        elif differentia_width == 1:
            assert hstrat.calc_rank_of_first_retained_disparity_between(
                c1, c2, 0.999999
            ) < hstrat.calc_rank_of_first_retained_disparity_between(
                c2, c1, 0.8
            )

    for c in [column, offspring1, offspring2]:
        for conf in 0.8, 0.95, 0.99:
            col_idx = (
                c.GetNumStrataRetained()
                - c.CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
                    significance_level=1 - conf,
                )
                + 1
            )
            if col_idx == c.GetNumStrataRetained():
                assert (
                    c.CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
                        significance_level=1 - conf,
                    )
                    == 1
                )
                assert (
                    hstrat.calc_rank_of_first_retained_disparity_between(
                        c, c, conf
                    )
                    is None
                )
            else:
                assert hstrat.calc_rank_of_first_retained_disparity_between(
                    c, c, conf
                ) == c.GetRankAtColumnIndex(col_idx)
