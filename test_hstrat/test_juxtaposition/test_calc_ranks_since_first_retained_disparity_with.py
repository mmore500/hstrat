from copy import deepcopy
import itertools as it
import random

from iterify import cyclify, iterify
import opytional as opyt
import pytest
from scipy import stats

from hstrat import hstrat


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
            stratum_ordered_store_factory=ordered_store,
            stratum_retention_policy=retention_policy,
        )
        for __ in range(10)
    ]

    for generation in range(100):
        for first, second in it.combinations(population, 2):
            rslcw = first.CalcRanksSinceLastRetainedCommonalityWith(second)
            if rslcw is not None:
                assert 0 <= rslcw <= generation

            rsfdw = hstrat.calc_ranks_since_first_retained_disparity_with(
                first, second
            )
            if rsfdw is not None:
                assert -1 <= rsfdw <= generation

            assert first.CalcRanksSinceMrcaBoundsWith(
                second
            ) is None or first.CalcRanksSinceMrcaBoundsWith(second) == (
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
        stratum_ordered_store_factory=ordered_store,
        stratum_retention_policy=retention_policy1,
    )
    second = hstrat.HereditaryStratigraphicColumn(
        stratum_ordered_store_factory=ordered_store,
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
        stratum_ordered_store_factory=ordered_store,
        stratum_retention_policy=retention_policy,
    )

    for generation in range(100):
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
        stratum_ordered_store_factory=ordered_store,
        stratum_retention_policy=retention_policy,
    )

    for generation in range(100):
        first.DepositStratum()

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

    for generation in range(100):
        column.DepositStratum()

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

    for generation in range(100):
        offspring1.DepositStratum()
        offspring2.DepositStratum()

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
