import os

import numpy as np
import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_aggregate_phylogenies,
    alifestd_assign_contiguous_ids,
    alifestd_find_leaf_ids,
    alifestd_prune_extinct_lineages_asexual,
    alifestd_to_working_format,
    alifestd_topological_sort,
    alifestd_try_add_ancestor_id_col,
    alifestd_unfurl_lineage_asexual,
    alifestd_validate,
)

assets_path = os.path.join(os.path.dirname(__file__), "assets")


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
        alifestd_assign_contiguous_ids,
        alifestd_to_working_format,
        alifestd_topological_sort,
        alifestd_try_add_ancestor_id_col,
        lambda x: x.sample(frac=1, random_state=1),
        lambda x: x,
    ],
)
def test_alifestd_prune_extinct_lineages_asexual_destruction_time_nop(
    phylogeny_df, apply
):

    assert "destruction_time" in phylogeny_df
    leaf_mask = phylogeny_df["id"].isin(
        {*alifestd_find_leaf_ids(phylogeny_df)}
    )
    leaf_destruction_times = phylogeny_df.loc[leaf_mask, "destruction_time"]
    assert (
        leaf_destruction_times.isna() | np.isinf(leaf_destruction_times)
    ).all()
    # because the source dataframes are pruned, pruning will be a nop
    phylogeny_df = apply(phylogeny_df.copy()).reset_index(drop=True)

    phylogeny_df_ = phylogeny_df.copy()
    pruned_df = alifestd_prune_extinct_lineages_asexual(phylogeny_df)
    assert phylogeny_df.equals(phylogeny_df_)

    assert len(phylogeny_df) == len(pruned_df)

    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df)
    assert {*phylogeny_df} == {*pruned_df}
    assert phylogeny_df.equals(pruned_df), phylogeny_df.compare(pruned_df)


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
        alifestd_assign_contiguous_ids,
        alifestd_to_working_format,
        alifestd_topological_sort,
        alifestd_try_add_ancestor_id_col,
        lambda x: x.sample(frac=1, random_state=1),
        lambda x: x,
    ],
)
def test_alifestd_prune_extinct_lineages_asexual(phylogeny_df, apply):
    # because the source dataframes are pruned, pruning will be a nop
    phylogeny_df = apply(phylogeny_df.copy())

    extant_mask = np.random.choice([True, False], size=len(phylogeny_df))
    phylogeny_df["extant"] = extant_mask

    phylogeny_df_ = phylogeny_df.copy()
    pruned_df = alifestd_prune_extinct_lineages_asexual(phylogeny_df)
    assert len(pruned_df) < len(phylogeny_df)
    assert set(pruned_df["id"]) >= set(phylogeny_df.loc[extant_mask, "id"])

    assert alifestd_validate(pruned_df)
    assert phylogeny_df.equals(phylogeny_df_)

    for leaf_id in alifestd_find_leaf_ids(pruned_df):
        assert [*alifestd_unfurl_lineage_asexual(phylogeny_df, leaf_id)] == [
            *alifestd_unfurl_lineage_asexual(pruned_df, leaf_id)
        ]


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
        alifestd_assign_contiguous_ids,
        alifestd_to_working_format,
        alifestd_topological_sort,
        alifestd_try_add_ancestor_id_col,
        lambda x: x.sample(frac=1, random_state=1),
        lambda x: x,
    ],
)
def test_alifestd_prune_extinct_lineages_asexual_independent_trees(
    phylogeny_df, apply
):
    # because the source dataframes are pruned, pruning will be a nop
    phylogeny_df = apply(phylogeny_df.copy())
    phylogeny_df["extant"] = False

    first_df = phylogeny_df.copy()
    extant_mask = first_df["id"].isin(alifestd_find_leaf_ids(first_df))
    first_df.loc[extant_mask, "extant"] = True

    second_df = phylogeny_df.copy()

    pruned_df = alifestd_prune_extinct_lineages_asexual(
        alifestd_aggregate_phylogenies([first_df, second_df]),
    )
    assert len(pruned_df) == len(phylogeny_df)


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
        alifestd_assign_contiguous_ids,
        alifestd_to_working_format,
        alifestd_topological_sort,
        alifestd_try_add_ancestor_id_col,
        lambda x: x.sample(frac=1, random_state=1),
        lambda x: x,
    ],
)
def test_alifestd_prune_extinct_lineages_asexual_ambiguous_extant(
    phylogeny_df, apply
):
    # because the source dataframes are pruned, pruning will be a nop
    phylogeny_df = apply(phylogeny_df.copy())
    phylogeny_df.drop("destruction_time", axis="columns", inplace=True)

    with pytest.raises(ValueError):
        alifestd_prune_extinct_lineages_asexual(phylogeny_df)
