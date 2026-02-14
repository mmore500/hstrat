import os
import typing

import numpy as np
import pandas as pd
import polars as pl
import pytest

from hstrat._auxiliary_lib import (
    alifestd_aggregate_phylogenies,
    alifestd_assign_contiguous_ids,
    alifestd_find_leaf_ids,
    alifestd_prune_extinct_lineages_asexual,
    alifestd_prune_extinct_lineages_polars,
    alifestd_to_working_format,
    alifestd_topological_sort,
    alifestd_try_add_ancestor_id_col,
)

assets_path = os.path.join(os.path.dirname(__file__), "assets")


@pytest.mark.parametrize(
    "phylogeny_df",
    [
        alifestd_to_working_format(
            pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv")
        ),
        alifestd_to_working_format(
            pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv")
        ),
        alifestd_to_working_format(
            alifestd_aggregate_phylogenies(
                [
                    pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
                    pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
                ]
            )
        ),
        alifestd_to_working_format(
            pd.read_csv(f"{assets_path}/nk_tournamentselection.csv")
        ),
    ],
)
@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_prune_extinct_lineages_polars_destruction_time_nop(
    phylogeny_df, apply: typing.Callable
):
    phylogeny_df_pl = apply(pl.from_pandas(phylogeny_df))

    pruned_df = (
        alifestd_prune_extinct_lineages_polars(phylogeny_df_pl)
        .lazy()
        .collect()
    )

    assert len(phylogeny_df) == len(pruned_df)


@pytest.mark.parametrize(
    "phylogeny_df",
    [
        alifestd_to_working_format(
            pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv")
        ),
        alifestd_to_working_format(
            pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv")
        ),
        alifestd_to_working_format(
            alifestd_aggregate_phylogenies(
                [
                    pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
                    pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
                ]
            )
        ),
        alifestd_to_working_format(
            pd.read_csv(f"{assets_path}/nk_tournamentselection.csv")
        ),
    ],
)
@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_prune_extinct_lineages_polars_extant(
    phylogeny_df, apply: typing.Callable
):
    phylogeny_df_pl = pl.from_pandas(phylogeny_df)

    np.random.seed(1)
    extant_mask = np.random.choice([True, False], size=len(phylogeny_df_pl))
    phylogeny_df_pl = phylogeny_df_pl.with_columns(
        extant=pl.Series(extant_mask),
    )
    phylogeny_df_pl = apply(phylogeny_df_pl)

    pruned_df = (
        alifestd_prune_extinct_lineages_polars(phylogeny_df_pl)
        .lazy()
        .collect()
    )
    assert len(pruned_df) < len(phylogeny_df)

    # all extant organisms must be in result
    extant_ids = set(
        pl.from_pandas(phylogeny_df)
        .with_columns(extant=pl.Series(extant_mask))
        .filter(pl.col("extant"))["id"]
        .to_list()
    )
    pruned_ids = set(pruned_df["id"].to_list())
    assert pruned_ids >= extant_ids


@pytest.mark.parametrize(
    "phylogeny_df",
    [
        alifestd_to_working_format(
            pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv")
        ),
        alifestd_to_working_format(
            pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv")
        ),
        alifestd_to_working_format(
            alifestd_aggregate_phylogenies(
                [
                    pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
                    pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
                ]
            )
        ),
        alifestd_to_working_format(
            pd.read_csv(f"{assets_path}/nk_tournamentselection.csv")
        ),
    ],
)
@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_prune_extinct_lineages_polars_matches_pandas(
    phylogeny_df, apply: typing.Callable
):
    """Verify polars result matches pandas result for same prepared input."""
    np.random.seed(1)
    extant_mask = np.random.choice([True, False], size=len(phylogeny_df))
    phylogeny_df["extant"] = extant_mask

    phylogeny_df_pl = apply(pl.from_pandas(phylogeny_df))

    # Run both implementations
    pruned_pd = alifestd_prune_extinct_lineages_asexual(
        phylogeny_df, mutate=False
    )
    pruned_pl = (
        alifestd_prune_extinct_lineages_polars(phylogeny_df_pl)
        .lazy()
        .collect()
    )

    # Compare the ids that are retained
    assert set(pruned_pd["id"]) == set(pruned_pl["id"].to_list())
    assert len(pruned_pd) == len(pruned_pl)


@pytest.mark.parametrize(
    "phylogeny_df",
    [
        pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
        pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
        alifestd_aggregate_phylogenies(
            [
                pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
                pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
            ]
        ),
        pd.read_csv(f"{assets_path}/nk_tournamentselection.csv"),
    ],
)
@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_prune_extinct_lineages_polars_independent_trees(
    phylogeny_df, apply: typing.Callable
):
    phylogeny_df_pd = alifestd_try_add_ancestor_id_col(phylogeny_df.copy())
    phylogeny_df_pd["extant"] = False

    first_df = phylogeny_df_pd.copy()
    leaf_ids = set(alifestd_find_leaf_ids(first_df))
    extant_mask = first_df["id"].isin(leaf_ids)
    first_df.loc[extant_mask, "extant"] = True

    second_df = phylogeny_df_pd.copy()

    aggregated = alifestd_aggregate_phylogenies([first_df, second_df])
    aggregated = alifestd_topological_sort(aggregated)
    aggregated = alifestd_assign_contiguous_ids(aggregated)

    aggregated_pl = apply(pl.from_pandas(aggregated))

    pruned_df = (
        alifestd_prune_extinct_lineages_polars(aggregated_pl)
        .lazy()
        .collect()
    )
    assert len(pruned_df) == len(phylogeny_df)


@pytest.mark.parametrize(
    "phylogeny_df",
    [
        alifestd_to_working_format(
            pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv")
        ),
        alifestd_to_working_format(
            pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv")
        ),
        alifestd_to_working_format(
            pd.read_csv(f"{assets_path}/nk_tournamentselection.csv")
        ),
    ],
)
@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_prune_extinct_lineages_polars_ambiguous_extant(
    phylogeny_df, apply: typing.Callable
):
    phylogeny_df_pl = apply(
        pl.from_pandas(phylogeny_df).drop("destruction_time")
    )

    with pytest.raises(ValueError):
        alifestd_prune_extinct_lineages_polars(phylogeny_df_pl).lazy().collect()


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_prune_extinct_lineages_polars_no_ancestor_id(
    apply: typing.Callable,
):
    df = apply(
        pl.DataFrame(
            {
                "id": [0, 1, 2],
                "ancestor_list": ["[none]", "[0]", "[1]"],
                "destruction_time": [float("inf")] * 3,
            }
        )
    )
    with pytest.raises(NotImplementedError):
        alifestd_prune_extinct_lineages_polars(df).lazy().collect()


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_prune_extinct_lineages_polars_noncontiguous(
    apply: typing.Callable,
):
    df = apply(
        pl.DataFrame(
            {
                "id": [0, 2, 5],
                "ancestor_id": [0, 0, 2],
                "destruction_time": [float("inf")] * 3,
            }
        )
    )
    with pytest.raises(NotImplementedError):
        alifestd_prune_extinct_lineages_polars(df).lazy().collect()


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_prune_extinct_lineages_polars_not_sorted(
    apply: typing.Callable,
):
    df = apply(
        pl.DataFrame(
            {
                "id": [0, 1, 2],
                "ancestor_id": [0, 2, 0],  # id 1 has ancestor 2 > 1
                "destruction_time": [float("inf")] * 3,
            }
        )
    )
    with pytest.raises(NotImplementedError):
        alifestd_prune_extinct_lineages_polars(df).lazy().collect()


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_prune_extinct_lineages_polars_empty(
    apply: typing.Callable,
):
    """Empty dataframe should return empty."""
    df = apply(
        pl.DataFrame(
            {"id": [], "ancestor_id": [], "destruction_time": []},
            schema={
                "id": pl.Int64,
                "ancestor_id": pl.Int64,
                "destruction_time": pl.Float64,
            },
        ),
    )

    result = alifestd_prune_extinct_lineages_polars(df).lazy().collect()
    assert result.is_empty()


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_prune_extinct_lineages_polars_simple(
    apply: typing.Callable,
):
    """Test a simple hand-crafted tree.

    Tree structure:
        0 (root)
        +-- 1
        |   +-- 3 (extant)
        |   +-- 4
        +-- 2
            +-- 5

    Only node 3 is extant, so nodes 0, 1, 3 should be kept.
    """
    df = apply(
        pl.DataFrame(
            {
                "id": [0, 1, 2, 3, 4, 5],
                "ancestor_id": [0, 0, 0, 1, 1, 2],
                "extant": [False, False, False, True, False, False],
            }
        )
    )

    pruned = alifestd_prune_extinct_lineages_polars(df).lazy().collect()

    assert set(pruned["id"].to_list()) == {0, 1, 3}
    assert len(pruned) == 3


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_prune_extinct_lineages_polars_all_extant(
    apply: typing.Callable,
):
    """When all nodes are extant, nothing should be pruned."""
    df = apply(
        pl.DataFrame(
            {
                "id": [0, 1, 2, 3],
                "ancestor_id": [0, 0, 1, 1],
                "extant": [True, True, True, True],
            }
        )
    )

    pruned = alifestd_prune_extinct_lineages_polars(df).lazy().collect()

    assert len(pruned) == 4


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_prune_extinct_lineages_polars_none_extant(
    apply: typing.Callable,
):
    """When no nodes are extant, everything should be pruned."""
    df = apply(
        pl.DataFrame(
            {
                "id": [0, 1, 2],
                "ancestor_id": [0, 0, 1],
                "extant": [False, False, False],
            }
        )
    )

    pruned = alifestd_prune_extinct_lineages_polars(df).lazy().collect()

    assert len(pruned) == 0
