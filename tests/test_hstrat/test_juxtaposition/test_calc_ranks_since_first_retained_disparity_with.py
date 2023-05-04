import itertools as it
import random

import opytional as opyt
import pytest

from hstrat import hstrat


@pytest.mark.parametrize(
    "retention_policy",
    [
        hstrat.perfect_resolution_algo.Policy(),
        hstrat.nominal_resolution_algo.Policy(),
        hstrat.fixed_resolution_algo.Policy(fixed_resolution=10),
        hstrat.recency_proportional_resolution_algo.Policy(
            recency_proportional_resolution=2
        ),
    ],
)
@pytest.mark.parametrize(
    "differentia_width",
    [1, 2, 8, 64],
)
def test_CalcRanksSinceFirstRetainedDisparityWith_specimen(
    retention_policy, differentia_width
):
    column = hstrat.HereditaryStratigraphicColumn(
        stratum_retention_policy=retention_policy,
        stratum_differentia_bit_width=differentia_width,
    )
    column2 = hstrat.HereditaryStratigraphicColumn(
        stratum_retention_policy=retention_policy,
        stratum_differentia_bit_width=differentia_width,
    )
    column.DepositStrata(100)

    child1 = column.CloneDescendant()
    child2 = column.CloneDescendant()

    assert hstrat.calc_ranks_since_first_retained_disparity_with(
        hstrat.col_to_specimen(column), hstrat.col_to_specimen(column2)
    ) == hstrat.calc_ranks_since_first_retained_disparity_with(column, column2)

    assert hstrat.calc_ranks_since_first_retained_disparity_with(
        hstrat.col_to_specimen(column), hstrat.col_to_specimen(column)
    ) == hstrat.calc_ranks_since_first_retained_disparity_with(column, column)

    assert hstrat.calc_ranks_since_first_retained_disparity_with(
        hstrat.col_to_specimen(column), hstrat.col_to_specimen(child1)
    ) == hstrat.calc_ranks_since_first_retained_disparity_with(column, child1)

    assert hstrat.calc_ranks_since_first_retained_disparity_with(
        hstrat.col_to_specimen(child1), hstrat.col_to_specimen(child2)
    ) == hstrat.calc_ranks_since_first_retained_disparity_with(child1, child2)

    child1.DepositStrata(10)
    assert hstrat.calc_ranks_since_first_retained_disparity_with(
        hstrat.col_to_specimen(child1), hstrat.col_to_specimen(child2)
    ) == hstrat.calc_ranks_since_first_retained_disparity_with(child1, child2)


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
def test_comparison_commutativity_synchronous(
    retention_policy,
    ordered_store,
):

    population = [
        hstrat.HereditaryStratigraphicColumn(
            stratum_ordered_store=ordered_store,
            stratum_retention_policy=retention_policy,
        )
        for __ in range(10)
    ]

    for _generation in range(100):
        _ = _generation
        for first, second in it.combinations(population, 2):
            # assert commutativity
            assert hstrat.calc_ranks_since_first_retained_disparity_with(
                first, second
            ) == hstrat.calc_ranks_since_first_retained_disparity_with(
                second, first
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
            stratum_ordered_store=ordered_store,
            stratum_retention_policy=retention_policy,
        )
        for __ in range(10)
    ]

    for generation in range(100):
        for first, second in it.combinations(population, 2):
            rslcw = hstrat.calc_ranks_since_last_retained_commonality_with(
                first, second
            )
            if rslcw is not None:
                assert 0 <= rslcw <= generation

            rsfdw = hstrat.calc_ranks_since_first_retained_disparity_with(
                first, second
            )
            if rsfdw is not None:
                assert -1 <= rsfdw <= generation

            assert hstrat.calc_ranks_since_mrca_bounds_with(
                first,
                second,
                prior="arbitrary",
            ) is None or hstrat.calc_ranks_since_mrca_bounds_with(
                first,
                second,
                prior="arbitrary",
            ) == (
                opyt.or_value(rsfdw, -1) + 1,
                rslcw + 1,
            )
            if rslcw is not None and rsfdw is not None:
                assert rsfdw < rslcw

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
        stratum_ordered_store=ordered_store,
        stratum_retention_policy=retention_policy1,
    )
    second = hstrat.HereditaryStratigraphicColumn(
        stratum_ordered_store=ordered_store,
        stratum_retention_policy=retention_policy2,
    )

    for generation in range(100):
        assert (
            hstrat.calc_ranks_since_first_retained_disparity_with(
                first, second
            )
            == generation
        )
        assert (
            hstrat.calc_ranks_since_first_retained_disparity_with(
                second, first
            )
            == generation
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
        stratum_ordered_store=ordered_store,
        stratum_retention_policy=retention_policy,
    )

    for _generation in range(100):
        _ = _generation
        assert (
            hstrat.calc_ranks_since_first_retained_disparity_with(
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
        stratum_ordered_store=ordered_store,
        stratum_retention_policy=retention_policy,
    )

    first.DepositStrata(100)

    second = first.Clone()

    first.DepositStratum()
    second.DepositStratum()

    for generation in range(101, 200):
        assert (
            0
            <= hstrat.calc_ranks_since_first_retained_disparity_with(
                first, second
            )
            < generation - 100
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
        stratum_ordered_store=ordered_store,
        stratum_retention_policy=retention_policy,
    )

    first.DepositStrata(100)

    second = first.Clone()

    first.DepositStratum()

    for generation in range(101, 200):
        assert (
            0
            <= hstrat.calc_ranks_since_first_retained_disparity_with(
                first, second
            )
            < generation - 100
        )
        assert -1 == hstrat.calc_ranks_since_first_retained_disparity_with(
            second, first
        )

        first.DepositStratum()

    second.DepositStratum()

    for generation in range(101, 200):
        assert (
            0
            <= hstrat.calc_ranks_since_first_retained_disparity_with(
                first, second
            )
            < 100
        )
        assert (
            -1
            <= hstrat.calc_ranks_since_first_retained_disparity_with(
                second, first
            )
            < generation - 100
        )

        second.DepositStratum()


@pytest.mark.parametrize(
    "differentia_width",
    [1, 2, 8, 64],
)
def test_CalcRanksSinceFirstRetainedDisparityWith1(differentia_width):
    column = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=differentia_width,
    )

    column.DepositStrata(100)

    offspring1 = column.CloneDescendant()
    offspring2 = column.CloneDescendant()

    for c1, c2 in it.combinations([column, offspring1, offspring2], 2):
        if differentia_width == 64:
            assert (
                hstrat.calc_ranks_since_first_retained_disparity_with(
                    c1,
                    c2,
                )
                == c1.GetNumStrataDeposited()
                - column.GetNumStrataDeposited()
                - 1
            )
            assert (
                hstrat.calc_ranks_since_first_retained_disparity_with(
                    c2,
                    c1,
                )
                == c2.GetNumStrataDeposited()
                - column.GetNumStrataDeposited()
                - 1
            )
        elif differentia_width == 1:
            assert (
                hstrat.calc_ranks_since_first_retained_disparity_with(
                    c1,
                    c2,
                )
                > c1.GetNumStrataDeposited()
                - column.GetNumStrataDeposited()
                - 1
            )
            assert (
                hstrat.calc_ranks_since_first_retained_disparity_with(
                    c2,
                    c1,
                )
                > c1.GetNumStrataDeposited()
                - column.GetNumStrataDeposited()
                - 1
            )

    for c in [column, offspring1, offspring2]:
        if (
            c.CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
                significance_level=0.2,
            )
            == 1
        ):
            assert (
                hstrat.calc_ranks_since_first_retained_disparity_with(
                    c, c, 0.8
                )
                is None
            )
        else:
            assert (
                hstrat.calc_ranks_since_first_retained_disparity_with(
                    c, c, 0.8
                )
                == c.CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
                    significance_level=0.2,
                )
                - 2
            ), (
                hstrat.calc_ranks_since_first_retained_disparity_with(
                    c, c, 0.8
                ),
                c.CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
                    significance_level=0.2,
                ),
            )

        if (
            c.CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
                significance_level=0.01,
            )
            == 1
        ):
            assert (
                hstrat.calc_ranks_since_first_retained_disparity_with(
                    c, c, 0.99
                )
                is None
            )
        else:
            assert (
                hstrat.calc_ranks_since_first_retained_disparity_with(
                    c, c, 0.99
                )
                == c.CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
                    significance_level=0.01,
                )
                - 2
            ), (
                hstrat.calc_ranks_since_first_retained_disparity_with(
                    c, c, 0.99
                ),
                c.CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
                    significance_level=0.01,
                ),
            )

    offspring1.DepositStrata(100)
    offspring2.DepositStrata(100)

    for c1, c2 in it.combinations([column, offspring1, offspring2], 2):
        if differentia_width == 64:
            assert (
                hstrat.calc_ranks_since_first_retained_disparity_with(
                    c1,
                    c2,
                )
                == c1.GetNumStrataDeposited()
                - column.GetNumStrataDeposited()
                - 1
            )
            assert (
                hstrat.calc_ranks_since_first_retained_disparity_with(
                    c2,
                    c1,
                )
                == c2.GetNumStrataDeposited()
                - column.GetNumStrataDeposited()
                - 1
            )
        elif differentia_width == 1:
            assert hstrat.calc_ranks_since_first_retained_disparity_with(
                c1, c2, 0.999999
            ) > hstrat.calc_ranks_since_first_retained_disparity_with(
                c1, c2, 0.8
            )

    for c in [column, offspring1, offspring2]:
        if (
            c.CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
                significance_level=0.2,
            )
            == 1
        ):
            assert (
                hstrat.calc_ranks_since_first_retained_disparity_with(
                    c, c, 0.8
                )
                is None
            )
        else:
            assert (
                hstrat.calc_ranks_since_first_retained_disparity_with(
                    c, c, 0.8
                )
                == c.CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
                    significance_level=0.2,
                )
                - 2
            ), (
                hstrat.calc_ranks_since_first_retained_disparity_with(
                    c, c, 0.8
                ),
                c.CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
                    significance_level=0.2,
                ),
            )

        if (
            c.CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
                significance_level=0.01,
            )
            == 1
        ):
            assert (
                hstrat.calc_ranks_since_first_retained_disparity_with(
                    c, c, 0.99
                )
                is None
            )
        else:
            assert (
                hstrat.calc_ranks_since_first_retained_disparity_with(
                    c, c, 0.99
                )
                == c.CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
                    significance_level=0.01,
                )
                - 2
            ), (
                hstrat.calc_ranks_since_first_retained_disparity_with(
                    c, c, 0.99
                ),
                c.CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
                    significance_level=0.01,
                ),
            )


@pytest.mark.parametrize(
    "differentia_width",
    # [1, 8, 64],
    [64],
)
@pytest.mark.parametrize(
    "policy",
    [
        hstrat.fixed_resolution_algo.Policy(3),
        # hstrat.recency_proportional_resolution_algo.Policy(1),
        # hstrat.nominal_resolution_algo.Policy(),
        # hstrat.perfect_resolution_algo.Policy(),
    ],
)
def test_artifact_types_equiv(differentia_width, policy):
    common_ancestor = hstrat.HereditaryStratigraphicColumn(
        stratum_retention_policy=policy,
        stratum_differentia_bit_width=differentia_width,
    ).CloneNthDescendant(7)
    c1 = common_ancestor.CloneNthDescendant(4)
    c2 = common_ancestor.CloneNthDescendant(9)
    c_x = hstrat.HereditaryStratigraphicColumn(
        stratum_retention_policy=policy,
        stratum_differentia_bit_width=differentia_width,
    ).CloneNthDescendant(7)
    c_y = hstrat.HereditaryStratigraphicColumn(
        stratum_retention_policy=policy,
        stratum_differentia_bit_width=differentia_width,
    )

    for a, b in it.product(
        [common_ancestor, c1, c2, c_x, c_y],
        [common_ancestor, c1, c2, c_x, c_y],
    ):
        assert hstrat.calc_ranks_since_first_retained_disparity_with(
            hstrat.col_to_specimen(a),
            hstrat.col_to_specimen(b),
        ) == hstrat.calc_ranks_since_first_retained_disparity_with(a, b)
