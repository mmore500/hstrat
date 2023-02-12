import itertools as it
import random

import numpy as np
import opytional as opyt
import pandas as pd
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
def test_build_distance_matrix_biopython_empty(
    differentia_bit_width,
    estimator,
    prior,
    force_common_ancestry,
):

    population = []
    dm = hstrat.build_distance_matrix_biopython(
        population,
        estimator,
        prior,
        force_common_ancestry=force_common_ancestry,
    )
    assert dm.matrix == []
    assert dm.names == []


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
    "names",
    [["foo"], None],
)
def test_build_distance_matrix_biopython_singleton(
    differentia_bit_width, estimator, prior, force_common_ancestry, names
):

    population = [hstrat.HereditaryStratigraphicColumn()]
    dm = hstrat.build_distance_matrix_biopython(
        population,
        estimator,
        prior,
        taxon_names=names,
        force_common_ancestry=force_common_ancestry,
    )
    m = hstrat.build_distance_matrix_numpy(
        population,
        estimator,
        prior,
        force_common_ancestry=force_common_ancestry,
    )
    assert np.array_equal(m, dm.matrix)
    assert opyt.or_value(names, ["0"]) == dm.names


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
    "names",
    [["foo", "bar"], None],
)
@pytest.mark.parametrize(
    "force_common_ancestry",
    [True, False],
)
def test_build_distance_matrix_biopython_pair_disjoint(
    differentia_bit_width,
    estimator,
    prior,
    names,
    force_common_ancestry,
):

    population = [
        hstrat.HereditaryStratigraphicColumn(),
        hstrat.HereditaryStratigraphicColumn(),
    ]
    dm = hstrat.build_distance_matrix_biopython(
        population,
        estimator,
        prior,
        taxon_names=names,
        force_common_ancestry=force_common_ancestry,
    )
    m = hstrat.build_distance_matrix_numpy(
        population,
        estimator,
        prior,
        force_common_ancestry=force_common_ancestry,
    )

    df_dm = pd.DataFrame(dm.matrix, dm.names)

    m[np.triu_indices(m.shape[0], 1)] = np.nan
    df_m = pd.DataFrame(m, opyt.or_value(names, ["0", "1"]))

    assert df_m.equals(df_dm)


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
    "names",
    [["foo", "bar"], None],
)
def test_build_distance_matrix_biopython_pair_disjoint2(
    differentia_bit_width,
    estimator,
    prior,
    names,
):

    population = [
        hstrat.HereditaryStratigraphicColumn(),
        hstrat.HereditaryStratigraphicColumn(),
    ]
    with pytest.raises(ValueError):
        dm = hstrat.build_distance_matrix_biopython(
            population,
            estimator,
            prior,
            taxon_names=names,
            force_common_ancestry=None,
        )


@pytest.mark.parametrize(
    "differentia_bit_width",
    [1, 2, 8, 64],
)
@pytest.mark.parametrize(
    "policy",
    [
        hstrat.fixed_resolution_algo.Policy(3),
        hstrat.perfect_resolution_algo.Policy(),
    ],
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
    "names",
    [["foo", "bar"], None],
)
@pytest.mark.parametrize(
    "force_common_ancestry",
    [True, False],
)
def test_build_distance_matrix_biopython_pair_commonancestry(
    differentia_bit_width,
    policy,
    estimator,
    prior,
    names,
    force_common_ancestry,
):

    common_ancestor = hstrat.HereditaryStratigraphicColumn(
        stratum_retention_policy=policy,
        stratum_differentia_bit_width=differentia_bit_width,
    ).CloneNthDescendant(7)
    population = [
        common_ancestor.CloneNthDescendant(4),
        common_ancestor.CloneNthDescendant(9),
    ]
    dm = hstrat.build_distance_matrix_biopython(
        population,
        estimator,
        prior,
        taxon_names=names,
        force_common_ancestry=force_common_ancestry,
    )
    m = hstrat.build_distance_matrix_numpy(
        population,
        estimator,
        prior,
        force_common_ancestry=force_common_ancestry,
    )

    df_dm = pd.DataFrame(dm.matrix, dm.names)

    m[np.triu_indices(m.shape[0], 1)] = np.nan
    df_m = pd.DataFrame(m, opyt.or_value(names, ["0", "1"]))

    assert df_m.equals(df_dm)
