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
        pytest.param(
            hstrat.HereditaryStratumOrderedStoreDict,
            marks=pytest.mark.heavy,
        ),
        hstrat.HereditaryStratumOrderedStoreList,
    ],
)
@pytest.mark.parametrize(
    "wrap",
    [lambda x: x, hstrat.col_to_specimen],
)
def test_comparison_commutativity_asynchronous(
    retention_policy,
    ordered_store,
    wrap,
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
            assert (
                hstrat.calc_rank_of_mrca_uncertainty_among(
                    [wrap(first), wrap(second)], prior="arbitrary"
                )
                == hstrat.calc_rank_of_mrca_uncertainty_among(
                    [wrap(second), wrap(first)], prior="arbitrary"
                )
                == hstrat.calc_rank_of_mrca_uncertainty_among(
                    [wrap(second), wrap(first), wrap(first)], prior="arbitrary"
                )
                == hstrat.calc_rank_of_mrca_uncertainty_among(
                    [wrap(second), wrap(first)] * 3, prior="arbitrary"
                )
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
@pytest.mark.parametrize(
    "wrap",
    [lambda x: x, hstrat.col_to_specimen],
)
def test_comparison_commutativity_synchronous(
    retention_policy,
    ordered_store,
    wrap,
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
            assert (
                hstrat.calc_rank_of_mrca_uncertainty_among(
                    [wrap(first), wrap(second)], prior="arbitrary"
                )
                == hstrat.calc_rank_of_mrca_uncertainty_among(
                    [wrap(second), wrap(first)], prior="arbitrary"
                )
                == hstrat.calc_rank_of_mrca_uncertainty_among(
                    [wrap(second), wrap(first), wrap(second)],
                    prior="arbitrary",
                )
                == hstrat.calc_rank_of_mrca_uncertainty_among(
                    [wrap(second), wrap(first)] * 3, prior="arbitrary"
                )
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
        pytest.param(
            hstrat.HereditaryStratumOrderedStoreDict,
            marks=pytest.mark.heavy,
        ),
        hstrat.HereditaryStratumOrderedStoreList,
    ],
)
@pytest.mark.parametrize(
    "wrap",
    [lambda x: x, hstrat.col_to_specimen],
)
def test_comparison_validity(retention_policy, ordered_store, wrap):
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
            assert (
                hstrat.calc_rank_of_mrca_uncertainty_among(
                    [wrap(first), wrap(second)], prior="arbitrary"
                )
                >= 0
            )
        for first, second, third in it.islice(
            it.combinations(population, 3), 100
        ):
            assert (
                hstrat.calc_rank_of_mrca_uncertainty_among(
                    [wrap(first), wrap(second), wrap(third)],
                    prior="arbitrary",
                )
                >= 0
            )

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
@pytest.mark.parametrize(
    "wrap",
    [lambda x: x, hstrat.col_to_specimen],
)
def test_scenario_no_mrca(
    retention_policy1,
    retention_policy2,
    ordered_store,
    wrap,
):
    first = hstrat.HereditaryStratigraphicColumn(
        stratum_ordered_store=ordered_store,
        stratum_retention_policy=retention_policy1,
    )
    second = hstrat.HereditaryStratigraphicColumn(
        stratum_ordered_store=ordered_store,
        stratum_retention_policy=retention_policy2,
    )

    for _generation in range(100):
        _ = _generation
        assert (
            hstrat.calc_rank_of_mrca_uncertainty_among(
                [wrap(first), wrap(second)],
                prior="arbitrary",
            )
            == 0
        )
        assert (
            hstrat.calc_rank_of_mrca_uncertainty_among(
                [wrap(second), wrap(first)],
                prior="arbitrary",
            )
            == 0
        )
        assert (
            hstrat.calc_rank_of_mrca_uncertainty_among(
                [wrap(first), wrap(second), wrap(first)],
                prior="arbitrary",
            )
            == 0
        )
        assert (
            hstrat.calc_rank_of_mrca_uncertainty_among(
                [wrap(second), wrap(first)] * 3,
                prior="arbitrary",
            )
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
        pytest.param(
            hstrat.HereditaryStratumOrderedStoreDict,
            marks=pytest.mark.heavy,
        ),
        hstrat.HereditaryStratumOrderedStoreList,
    ],
)
@pytest.mark.parametrize(
    "wrap",
    [lambda x: x, hstrat.col_to_specimen],
)
def test_scenario_no_divergence(retention_policy, ordered_store, wrap):
    column = hstrat.HereditaryStratigraphicColumn(
        stratum_ordered_store=ordered_store,
        stratum_retention_policy=retention_policy,
    )

    for _generation in range(100):
        _ = _generation
        assert (
            hstrat.calc_rank_of_mrca_uncertainty_among(
                [wrap(column), wrap(column)],
                prior="arbitrary",
            )
            == 0
        )
        assert (
            hstrat.calc_rank_of_mrca_uncertainty_among(
                [wrap(column), wrap(column), wrap(column)],
                prior="arbitrary",
            )
            == 0
        )
        assert (
            hstrat.calc_rank_of_mrca_uncertainty_among(
                [wrap(column), wrap(column)] * 3, prior="arbitrary"
            )
            == 0
        )
        column.DepositStratum()


@pytest.mark.parametrize(
    "retention_policy",
    [
        hstrat.perfect_resolution_algo.Policy(),
        hstrat.fixed_resolution_algo.Policy(fixed_resolution=10),
        hstrat.recency_proportional_resolution_algo.Policy(
            recency_proportional_resolution=10,
        ),
    ],
)
@pytest.mark.parametrize(
    "differentia_width",
    [1, 2, 8, 64],
)
@pytest.mark.parametrize(
    "confidence_level",
    [0.8, 0.95],
)
@pytest.mark.parametrize(
    "wrap",
    [
        lambda x: x,
        pytest.param(
            hstrat.col_to_specimen,
            marks=pytest.mark.heavy,
        ),
    ],
)
def test_CalcRankOfMrcaUncertaintyWith_narrow_shallow(
    retention_policy,
    differentia_width,
    confidence_level,
    wrap,
):

    columns = [
        hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=differentia_width,
            stratum_retention_policy=retention_policy,
            stratum_ordered_store=hstrat.HereditaryStratumOrderedStoreDict,
        )
        for __ in range(20)
    ]

    steps = list(
        range(
            columns[
                0
            ].CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
                significance_level=1 - confidence_level,
            )
            - columns[0].GetNumStrataDeposited()
        )
    )

    for step1, step2 in it.product(steps, steps):
        column1 = [col.Clone() for col in columns]
        column2 = [col.Clone() for col in columns]
        column3 = [col.Clone() for col in columns]
        for __ in range(step1):
            for col in column1:
                col.DepositStratum()
        for __ in range(step2):
            for col in column2:
                col.DepositStratum()
        for __ in range(step1):
            for col in column2:
                col.DepositStratum()

        for c1, c2 in zip(column1, column2):
            assert (
                hstrat.calc_rank_of_mrca_uncertainty_among(
                    [wrap(c1), wrap(c2)],
                    prior="arbitrary",
                    confidence_level=confidence_level,
                )
                is None
            )
            assert (
                hstrat.calc_rank_of_mrca_uncertainty_among(
                    [wrap(c2), wrap(c1)],
                    prior="arbitrary",
                    confidence_level=confidence_level,
                )
                is None
            )
        for c1, c2, c3 in zip(column1, column2, column3):
            assert (
                hstrat.calc_rank_of_mrca_uncertainty_among(
                    [wrap(c1), wrap(c2), wrap(c3)],
                    prior="arbitrary",
                    confidence_level=confidence_level,
                )
                is None
            )
            assert (
                hstrat.calc_rank_of_mrca_uncertainty_among(
                    [wrap(c2), wrap(c3), wrap(c1)],
                    prior="arbitrary",
                    confidence_level=confidence_level,
                )
                is None
            )


@pytest.mark.parametrize(
    "retention_policy",
    [
        hstrat.perfect_resolution_algo.Policy(),
        hstrat.fixed_resolution_algo.Policy(fixed_resolution=10),
        hstrat.recency_proportional_resolution_algo.Policy(
            recency_proportional_resolution=10,
        ),
    ],
)
@pytest.mark.parametrize(
    "differentia_width",
    [1, 2, 8, 64],
)
@pytest.mark.parametrize(
    "confidence_level",
    [0.8, 0.95],
)
@pytest.mark.parametrize(
    "mrca_rank",
    [100],
)
@pytest.mark.parametrize(
    "wrap",
    [
        lambda x: x,
        pytest.param(
            hstrat.col_to_specimen,
            marks=pytest.mark.heavy,
        ),
    ],
)
def test_CalcRankOfMrcaUncertaintyWith_narrow_with_mrca(
    retention_policy,
    differentia_width,
    confidence_level,
    mrca_rank,
    wrap,
):

    columns = [
        hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=differentia_width,
            stratum_retention_policy=retention_policy,
            stratum_ordered_store=hstrat.HereditaryStratumOrderedStoreDict,
        )
        for __ in range(20)
    ]

    for column in columns:
        column.DepositStrata(mrca_rank)

    steps = (0, 16, 51)

    for step1, step2 in it.product(steps, steps):
        column1 = [col.Clone() for col in columns]
        column2 = [col.Clone() for col in columns]
        for __ in range(step1):
            for col in column1:
                col.DepositStratum()
        for i in range(step2):
            for col in column2:
                col.DepositStratum()

        for c1, c2 in zip(column1, column2):
            assert hstrat.calc_rank_of_mrca_uncertainty_among(
                [wrap(c1), wrap(c2)],
                prior="arbitrary",
                confidence_level=confidence_level,
            ) == hstrat.calc_rank_of_mrca_uncertainty_among(
                [wrap(c2), wrap(c1)],
                prior="arbitrary",
                confidence_level=confidence_level,
            )
            res = hstrat.calc_rank_of_mrca_uncertainty_among(
                [wrap(c1), wrap(c2)],
                prior="arbitrary",
                confidence_level=confidence_level,
            )

            if res is not None:
                assert res >= 0
                assert hstrat.calc_rank_of_mrca_uncertainty_among(
                    [wrap(c1), wrap(c2)],
                    prior="arbitrary",
                    confidence_level=confidence_level,
                ) >= hstrat.calc_rank_of_mrca_uncertainty_among(
                    [wrap(c2), wrap(c1)],
                    prior="arbitrary",
                    confidence_level=confidence_level / 2,
                )

    for step1, step2 in it.product(steps, steps):
        column1 = [col.Clone() for col in columns]
        column2 = [col.Clone() for col in columns]
        column3 = [col.Clone() for col in columns]
        for __ in range(step1):
            for col in column1:
                col.DepositStratum()
        for i in range(step2):
            for col in column2:
                col.DepositStratum()
        for i in range(step1):
            for col in column3:
                col.DepositStratum()

        for c1, c2, c3 in zip(column1, column2, column3):
            assert hstrat.calc_rank_of_mrca_uncertainty_among(
                [wrap(c1), wrap(c2), wrap(c3)],
                prior="arbitrary",
                confidence_level=confidence_level,
            ) == hstrat.calc_rank_of_mrca_uncertainty_among(
                [wrap(c2), wrap(c1), wrap(c3)],
                prior="arbitrary",
                confidence_level=confidence_level,
            )
            res = hstrat.calc_rank_of_mrca_uncertainty_among(
                [wrap(c1), wrap(c2), wrap(c3)],
                prior="arbitrary",
                confidence_level=confidence_level,
            )

            if res is not None:
                assert res >= 0
                assert hstrat.calc_rank_of_mrca_uncertainty_among(
                    [wrap(c1), wrap(c2), wrap(c3)],
                    prior="arbitrary",
                    confidence_level=confidence_level,
                ) >= hstrat.calc_rank_of_mrca_uncertainty_among(
                    [wrap(c2), wrap(c1), wrap(c3)],
                    prior="arbitrary",
                    confidence_level=confidence_level / 2,
                )


@pytest.mark.parametrize(
    "retention_policy",
    [
        hstrat.perfect_resolution_algo.Policy(),
        hstrat.fixed_resolution_algo.Policy(fixed_resolution=10),
        hstrat.recency_proportional_resolution_algo.Policy(
            recency_proportional_resolution=10,
        ),
    ],
)
@pytest.mark.parametrize(
    "differentia_width",
    [1, 2, 8, 64],
)
@pytest.mark.parametrize(
    "confidence_level",
    [0.8, 0.95],
)
@pytest.mark.parametrize(
    "mrca_rank",
    [0, 100],
)
@pytest.mark.parametrize(
    "wrap",
    [
        lambda x: x,
        pytest.param(
            hstrat.col_to_specimen,
            marks=pytest.mark.heavy,
        ),
    ],
)
def test_CalcRankOfMrcaUncertaintyWith_narrow_no_mrca(
    retention_policy,
    differentia_width,
    confidence_level,
    mrca_rank,
    wrap,
):
    def make_column():
        return hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=differentia_width,
            stratum_retention_policy=retention_policy,
            stratum_ordered_store=hstrat.HereditaryStratumOrderedStoreDict,
        )

    columns = [make_column() for __ in range(20)]

    for column in columns:
        column.DepositStrata(mrca_rank)

    steps = (0, 16, 51)

    for step1, step2 in it.product(steps, steps):
        column1 = [make_column() for col in columns]
        column2 = [make_column() for col in columns]
        column3 = [make_column() for col in columns]
        for __ in range(step1):
            for col in column1:
                col.DepositStratum()
        for i in range(step2):
            for col in column2:
                col.DepositStratum()
        for i in range(step1):
            for col in column3:
                col.DepositStratum()

        for c1, c2 in zip(column1, column2):
            assert hstrat.calc_rank_of_mrca_uncertainty_among(
                [wrap(c1), wrap(c2)],
                prior="arbitrary",
                confidence_level=confidence_level,
            ) == hstrat.calc_rank_of_mrca_uncertainty_among(
                [wrap(c2), wrap(c1)],
                prior="arbitrary",
                confidence_level=confidence_level,
            )
            res = hstrat.calc_rank_of_mrca_uncertainty_among(
                [wrap(c1), wrap(c2)],
                prior="arbitrary",
                confidence_level=confidence_level,
            )

            if res is not None:
                assert 0 <= res
                assert (
                    hstrat.calc_rank_of_mrca_uncertainty_among(
                        [wrap(c1), wrap(c2)],
                        prior="arbitrary",
                        confidence_level=confidence_level,
                    )
                    >= hstrat.calc_rank_of_mrca_uncertainty_among(
                        [wrap(c2), wrap(c1)],
                        prior="arbitrary",
                        confidence_level=confidence_level / 2,
                    )
                    or hstrat.calc_rank_of_mrca_uncertainty_among(
                        [wrap(c1), wrap(c2)],
                        prior="arbitrary",
                        confidence_level=confidence_level,
                    )
                    == 0
                )

        for c1, c2, c3 in zip(column1, column2, column3):
            assert hstrat.calc_rank_of_mrca_uncertainty_among(
                [wrap(c1), wrap(c2), wrap(c3)],
                prior="arbitrary",
                confidence_level=confidence_level,
            ) == hstrat.calc_rank_of_mrca_uncertainty_among(
                [wrap(c3), wrap(c1), wrap(c2)],
                prior="arbitrary",
                confidence_level=confidence_level,
            )
            res = hstrat.calc_rank_of_mrca_uncertainty_among(
                [wrap(c1), wrap(c2), wrap(c3)],
                prior="arbitrary",
                confidence_level=confidence_level,
            )

            if res is not None:
                assert 0 <= res
                assert (
                    hstrat.calc_rank_of_mrca_uncertainty_among(
                        [wrap(c1), wrap(c2), wrap(c3)],
                        prior="arbitrary",
                        confidence_level=confidence_level,
                    )
                    >= hstrat.calc_rank_of_mrca_uncertainty_among(
                        [wrap(c1), wrap(c2), wrap(c3)],
                        prior="arbitrary",
                        confidence_level=confidence_level / 2,
                    )
                    or hstrat.calc_rank_of_mrca_uncertainty_among(
                        [wrap(c1), wrap(c2), wrap(c3)],
                        prior="arbitrary",
                        confidence_level=confidence_level,
                    )
                    == 0
                )


@pytest.mark.filterwarnings("ignore:Empty or singleton population.")
@pytest.mark.parametrize(
    "wrap",
    [lambda x: x, hstrat.col_to_specimen],
)
def test_calc_rank_of_mrca_uncertainty_among_singleton(wrap):
    c1 = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=1,
    )
    for __ in range(10):
        assert (
            hstrat.calc_rank_of_mrca_uncertainty_among(
                [wrap(c1)], prior="arbitrary"
            )
            is None
        )
        c1.DepositStratum()

    c2 = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=64,
    )
    for __ in range(10):
        assert (
            hstrat.calc_rank_of_mrca_uncertainty_among(
                [wrap(c1)], prior="arbitrary"
            )
            is None
        )
        c2.DepositStratum()


@pytest.mark.filterwarnings("ignore:Empty or singleton population.")
def test_calc_rank_of_mrca_uncertainty_among_empty():
    assert (
        hstrat.calc_rank_of_mrca_uncertainty_among([], prior="arbitrary")
        is None
    )


@pytest.mark.parametrize(
    "wrap",
    [lambda x: x, hstrat.col_to_specimen],
)
def test_calc_rank_of_mrca_uncertainty_among_generator(wrap):
    c1 = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=1,
    )
    for __ in range(10):
        assert hstrat.calc_rank_of_mrca_uncertainty_among(
            [wrap(c1) for __ in range(10)], prior="arbitrary"
        ) == hstrat.calc_rank_of_mrca_uncertainty_among(
            (wrap(c1) for __ in range(10)), prior="arbitrary"
        )
        c1.DepositStratum()

    c2 = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=64,
    )
    for __ in range(10):
        assert hstrat.calc_rank_of_mrca_uncertainty_among(
            [wrap(c2) for __ in range(10)], prior="arbitrary"
        ) == hstrat.calc_rank_of_mrca_uncertainty_among(
            (wrap(c2) for __ in range(10)), prior="arbitrary"
        )
        c2.DepositStratum()
