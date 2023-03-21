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
@pytest.mark.parametrize(
    "wrap",
    [lambda x: x, hstrat.col_to_specimen],
)
def test_build_distance_matrix_biopython_singleton(
    differentia_bit_width, estimator, prior, force_common_ancestry, names, wrap
):

    population = [wrap(hstrat.HereditaryStratigraphicColumn())]
    dm = hstrat.build_distance_matrix_biopython(
        population,
        estimator,
        prior,
        taxon_labels=names,
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
@pytest.mark.parametrize(
    "wrap",
    [lambda x: x, hstrat.col_to_specimen],
)
def test_build_distance_matrix_biopython_pair_disjoint(
    differentia_bit_width,
    estimator,
    prior,
    names,
    force_common_ancestry,
    wrap,
):

    population = [
        wrap(hstrat.HereditaryStratigraphicColumn()),
        wrap(hstrat.HereditaryStratigraphicColumn()),
    ]
    dm = hstrat.build_distance_matrix_biopython(
        population,
        estimator,
        prior,
        taxon_labels=names,
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
@pytest.mark.parametrize(
    "wrap",
    [lambda x: x, hstrat.col_to_specimen],
)
def test_build_distance_matrix_biopython_pair_disjoint2(
    differentia_bit_width,
    estimator,
    prior,
    names,
    wrap,
):

    population = [
        wrap(hstrat.HereditaryStratigraphicColumn()),
        wrap(hstrat.HereditaryStratigraphicColumn()),
    ]
    with pytest.raises(ValueError):
        hstrat.build_distance_matrix_biopython(
            population,
            estimator,
            prior,
            taxon_labels=names,
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
@pytest.mark.parametrize(
    "wrap",
    [lambda x: x, hstrat.col_to_specimen],
)
def test_build_distance_matrix_biopython_pair_commonancestry(
    differentia_bit_width,
    policy,
    estimator,
    prior,
    names,
    force_common_ancestry,
    wrap,
):

    common_ancestor = hstrat.HereditaryStratigraphicColumn(
        stratum_retention_policy=policy,
        stratum_differentia_bit_width=differentia_bit_width,
    ).CloneNthDescendant(7)
    population = [
        wrap(common_ancestor.CloneNthDescendant(4)),
        wrap(common_ancestor.CloneNthDescendant(9)),
    ]
    dm = hstrat.build_distance_matrix_biopython(
        population,
        estimator,
        prior,
        taxon_labels=names,
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
    [["foo", "bar"]],
)
@pytest.mark.parametrize(
    "force_common_ancestry",
    [True, False],
)
@pytest.mark.parametrize(
    "wrap",
    [lambda x: x, hstrat.col_to_specimen],
)
def test_build_distance_matrix_biopython_pair_iternames(
    differentia_bit_width,
    policy,
    estimator,
    prior,
    names,
    force_common_ancestry,
    wrap,
):

    common_ancestor = hstrat.HereditaryStratigraphicColumn(
        stratum_retention_policy=policy,
        stratum_differentia_bit_width=differentia_bit_width,
    ).CloneNthDescendant(7)
    population = [
        wrap(common_ancestor.CloneNthDescendant(4)),
        wrap(common_ancestor.CloneNthDescendant(9)),
    ]
    dm = hstrat.build_distance_matrix_biopython(
        population,
        estimator,
        prior,
        taxon_labels=opyt.apply_if(names, iter),
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
    "policy",
    [
        hstrat.fixed_resolution_algo.Policy(3),
        hstrat.recency_proportional_resolution_algo.Policy(4),
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
def test_build_distance_matrix_biopython_pair_artifact_types_equiv(
    policy, estimator, prior
):

    common_ancestor = hstrat.HereditaryStratigraphicColumn(
        stratum_retention_policy=policy,
    ).CloneNthDescendant(7)
    population = [
        common_ancestor.CloneNthDescendant(4),
        common_ancestor.CloneNthDescendant(9),
    ]
    dm_column = hstrat.build_distance_matrix_biopython(
        population,
        estimator,
        prior,
    )
    dm_specimen = hstrat.build_distance_matrix_biopython(
        [*map(hstrat.col_to_specimen, population)],
        estimator,
        prior,
    )

    df_dm_column = pd.DataFrame(dm_column.matrix, dm_column.names)
    df_dm_specimen = pd.DataFrame(dm_specimen.matrix, dm_specimen.names)

    assert df_dm_column.equals(df_dm_specimen)
