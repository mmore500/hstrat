import random

import numpy as np
import pytest

from hstrat import hstrat


@pytest.mark.parametrize(
    "differentia_bit_width",
    [1, 2, 8, 64],
)
@pytest.mark.parametrize(
    "estimator",
    ["maximum_likelihood", "unbiased"],
)
@pytest.mark.parametrize(
    "prior",
    ["arbitrary", "uniform"],
)
@pytest.mark.parametrize(
    "force_common_ancestry",
    [True, False, None],
)
def test_build_distance_matrix_numpy_empty(
    differentia_bit_width,
    estimator,
    prior,
    force_common_ancestry,
):

    population = []
    assert np.array_equal(
        hstrat.build_distance_matrix_numpy(
            population,
            estimator,
            prior,
            force_common_ancestry,
        ),
        np.zeros((0, 0)),
    )


@pytest.mark.parametrize(
    "differentia_bit_width",
    [1, 2, 8, 64],
)
@pytest.mark.parametrize(
    "estimator",
    ["maximum_likelihood", "unbiased"],
)
@pytest.mark.parametrize(
    "prior",
    ["arbitrary", "uniform"],
)
@pytest.mark.parametrize(
    "force_common_ancestry",
    [True, False, None],
)
@pytest.mark.parametrize(
    "wrap",
    [lambda x: x, hstrat.col_to_specimen],
)
def test_build_distance_matrix_numpy_singleton(
    differentia_bit_width,
    estimator,
    prior,
    force_common_ancestry,
    wrap,
):

    population = [wrap(hstrat.HereditaryStratigraphicColumn())]
    assert np.array_equal(
        hstrat.build_distance_matrix_numpy(
            population,
            estimator,
            prior,
            force_common_ancestry,
        ),
        np.array([[0.0]]),
    )


@pytest.mark.filterwarnings(
    "ignore:Insufficient common ranks between columns to detect common ancestry at given confidence level."
)
@pytest.mark.parametrize(
    "differentia_bit_width",
    [64],
)
@pytest.mark.parametrize(
    "estimator",
    [
        "maximum_likelihood",
        "unbiased",
    ],
)
@pytest.mark.parametrize(
    "prior",
    ["arbitrary", "uniform"],
)
@pytest.mark.parametrize(
    "wrap",
    [lambda x: x, hstrat.col_to_specimen],
)
def test_build_distance_matrix_numpy_pair_unrelated(
    differentia_bit_width,
    estimator,
    prior,
    wrap,
):

    population = [
        wrap(hstrat.HereditaryStratigraphicColumn()),
        wrap(hstrat.HereditaryStratigraphicColumn()),
    ]
    assert np.array_equal(
        hstrat.build_distance_matrix_numpy(
            population,
            estimator,
            prior,
            force_common_ancestry=True,
        ),
        np.array([[0.0, 2.0], [2.0, 0.0]]),
    )
    assert np.array_equal(
        hstrat.build_distance_matrix_numpy(
            population,
            estimator,
            prior,
            force_common_ancestry=False,
        ),
        np.array([[0.0, np.nan], [np.nan, 0.0]]),
        equal_nan=True,
    )
    with pytest.raises(ValueError):
        hstrat.build_distance_matrix_numpy(
            population,
            estimator,
            prior,
            force_common_ancestry=None,
        )


@pytest.mark.parametrize(
    "generations_before_mrca",
    [0, 8],
)
@pytest.mark.parametrize(
    "first_generations_since_mrca",
    [0, 5],
)
@pytest.mark.parametrize(
    "second_generations_since_mrca",
    [0, 5],
)
@pytest.mark.parametrize(
    "differentia_bit_width",
    [1, 8, 64],
)
@pytest.mark.parametrize(
    "estimator",
    [
        "maximum_likelihood",
        "unbiased",
    ],
)
@pytest.mark.parametrize(
    "prior",
    ["arbitrary", "uniform", hstrat.GeometricPrior(1.1)],
)
@pytest.mark.parametrize(
    "force_common_ancestry",
    [True, False, None],
)
@pytest.mark.parametrize(
    "wrap",
    [lambda x: x, hstrat.col_to_specimen],
)
def test_build_distance_matrix_numpy_pair_related(
    generations_before_mrca,
    first_generations_since_mrca,
    second_generations_since_mrca,
    differentia_bit_width,
    estimator,
    prior,
    force_common_ancestry,
    wrap,
):

    if differentia_bit_width == 64:
        common_ancestor = hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=differentia_bit_width
        ).CloneNthDescendant(generations_before_mrca)
        population = [
            wrap(
                common_ancestor.CloneNthDescendant(
                    first_generations_since_mrca
                )
            ),
            wrap(
                common_ancestor.CloneNthDescendant(
                    second_generations_since_mrca
                )
            ),
        ]
        expected_patristic_distance = (
            first_generations_since_mrca + second_generations_since_mrca
        )
        assert np.isclose(
            hstrat.build_distance_matrix_numpy(
                population,
                estimator,
                prior,
                force_common_ancestry=force_common_ancestry,
            ),
            np.array(
                [
                    [0.0, expected_patristic_distance],
                    [expected_patristic_distance, 0.0],
                ]
            ),
        ).all()

    common_ancestor = hstrat.HereditaryStratigraphicColumn(
        stratum_retention_policy=hstrat.fixed_resolution_algo.Policy(3),
        stratum_differentia_bit_width=differentia_bit_width,
    ).CloneNthDescendant(generations_before_mrca)
    population = [
        wrap(common_ancestor.CloneNthDescendant(first_generations_since_mrca)),
        wrap(
            common_ancestor.CloneNthDescendant(second_generations_since_mrca)
        ),
    ]
    expected_patristic_distance = hstrat.estimate_patristic_distance_between(
        *population,
        estimator=estimator,
        prior=prior,
    )
    assert np.isclose(
        hstrat.build_distance_matrix_numpy(
            population,
            estimator=estimator,
            prior=prior,
            force_common_ancestry=force_common_ancestry,
        ),
        np.array(
            [
                [0.0, expected_patristic_distance],
                [expected_patristic_distance, 0.0],
            ]
        ),
    ).all()


@pytest.mark.parametrize(
    "generations_before_mrca",
    [0, 8],
)
@pytest.mark.parametrize(
    "first_generations_since_mrca",
    [0, 5],
)
@pytest.mark.parametrize(
    "second_generations_since_mrca",
    [0, 5],
)
@pytest.mark.parametrize(
    "differentia_bit_width",
    [64],
)
@pytest.mark.parametrize(
    "estimator",
    [
        "maximum_likelihood",
        "unbiased",
    ],
)
@pytest.mark.parametrize(
    "prior",
    ["arbitrary", "uniform", hstrat.GeometricPrior(1.1)],
)
@pytest.mark.parametrize(
    "force_common_ancestry",
    [True, False, None],
)
@pytest.mark.parametrize(
    "wrap",
    [lambda x: x, hstrat.col_to_specimen],
)
def test_build_distance_matrix_numpy_pair_and_unrelated(
    generations_before_mrca,
    first_generations_since_mrca,
    second_generations_since_mrca,
    differentia_bit_width,
    estimator,
    prior,
    force_common_ancestry,
    wrap,
):

    common_ancestor = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=differentia_bit_width
    ).CloneNthDescendant(generations_before_mrca)
    population = [
        wrap(common_ancestor.CloneNthDescendant(first_generations_since_mrca)),
        wrap(
            common_ancestor.CloneNthDescendant(second_generations_since_mrca)
        ),
        wrap(
            hstrat.HereditaryStratigraphicColumn(
                stratum_differentia_bit_width=differentia_bit_width
            )
        ),
    ]
    expected_patristic_distance = (
        first_generations_since_mrca + second_generations_since_mrca
    )
    assert np.array_equal(
        hstrat.build_distance_matrix_numpy(
            population,
            estimator,
            prior,
            force_common_ancestry=False,
        ),
        np.array(
            [
                [0.0, expected_patristic_distance, np.nan],
                [expected_patristic_distance, 0.0, np.nan],
                [np.nan, np.nan, 0.0],
            ]
        ),
        equal_nan=True,
    )

    max_patristic_distance0to2 = (
        population[0].GetNumStrataDeposited()
        + population[2].GetNumStrataDeposited()
    )
    max_patristic_distance1to2 = (
        population[1].GetNumStrataDeposited()
        + population[2].GetNumStrataDeposited()
    )
    assert np.array_equal(
        hstrat.build_distance_matrix_numpy(
            population,
            estimator,
            prior,
            force_common_ancestry=True,
        ),
        np.array(
            [
                [0.0, expected_patristic_distance, max_patristic_distance0to2],
                [expected_patristic_distance, 0.0, max_patristic_distance1to2],
                [max_patristic_distance0to2, max_patristic_distance1to2, 0.0],
            ]
        ),
    )


@pytest.mark.parametrize(
    "generations_before_mrca",
    [0, 8],
)
@pytest.mark.parametrize(
    "differentia_bit_width",
    [1, 8, 64],
)
@pytest.mark.parametrize(
    "estimator",
    [
        "maximum_likelihood",
        "unbiased",
    ],
)
@pytest.mark.parametrize(
    "prior",
    ["arbitrary", "uniform", hstrat.GeometricPrior(1.1)],
)
@pytest.mark.parametrize(
    "force_common_ancestry",
    [True, False, None],
)
@pytest.mark.parametrize(
    "replicate",
    range(20),
)
@pytest.mark.parametrize(
    "wrap",
    [lambda x: x, hstrat.col_to_specimen],
)
def test_build_distance_matrix_numpy_triple(
    generations_before_mrca,
    differentia_bit_width,
    estimator,
    prior,
    force_common_ancestry,
    replicate,
    wrap,
):

    common_ancestor = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=differentia_bit_width
    ).CloneNthDescendant(generations_before_mrca)
    population = [
        wrap(common_ancestor.CloneNthDescendant(random.randrange(0, 4))),
        wrap(common_ancestor.CloneNthDescendant(random.randrange(0, 4))),
        wrap(common_ancestor.CloneNthDescendant(random.randrange(0, 4))),
    ]

    d01 = hstrat.estimate_patristic_distance_between(
        population[0], population[1], estimator, prior
    )
    d02 = hstrat.estimate_patristic_distance_between(
        population[0], population[2], estimator, prior
    )
    d12 = hstrat.estimate_patristic_distance_between(
        population[1], population[2], estimator, prior
    )
    assert np.array_equal(
        hstrat.build_distance_matrix_numpy(
            population,
            estimator,
            prior,
            force_common_ancestry=force_common_ancestry,
        ),
        np.array(
            [
                [0.0, d01, d02],
                [d01, 0.0, d12],
                [d02, d12, 0.0],
            ]
        ),
        equal_nan=True,
    )
