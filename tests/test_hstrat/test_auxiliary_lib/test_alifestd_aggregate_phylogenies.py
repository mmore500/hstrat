from collections import Counter
import os

import alifedata_phyloinformatics_convert as apc
import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_aggregate_phylogenies,
    alifestd_find_leaf_ids,
    alifestd_has_contiguous_ids,
    alifestd_is_asexual,
    alifestd_is_sexual,
    alifestd_is_topologically_sorted,
    alifestd_make_ancestor_id_col,
    alifestd_to_working_format,
    alifestd_try_add_ancestor_id_col,
    alifestd_validate,
)

assets_path = os.path.join(os.path.dirname(__file__), "assets")


@pytest.mark.parametrize(
    "phylogeny_df1",
    [
        pd.read_csv(
            f"{assets_path}/example-standard-toy-sexual-phylogeny.csv"
        ),
        pd.read_csv(
            f"{assets_path}/example-standard-toy-asexual-phylogeny.csv"
        ),
        pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
        pd.read_csv(f"{assets_path}/nk_tournamentselection.csv"),
        pd.read_csv(f"{assets_path}/nk_tournamentselection.csv")[-1:0],
    ],
)
@pytest.mark.parametrize(
    "phylogeny_df2",
    [
        pd.read_csv(
            f"{assets_path}/example-standard-toy-sexual-phylogeny.csv"
        ),
        pd.read_csv(
            f"{assets_path}/example-standard-toy-asexual-phylogeny.csv"
        ),
        pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
        pd.read_csv(f"{assets_path}/nk_tournamentselection.csv"),
        pd.read_csv(f"{assets_path}/nk_tournamentselection.csv")[-1:0],
        None,
    ],
)
@pytest.mark.parametrize(
    "phylogeny_df3",
    [
        pd.read_csv(
            f"{assets_path}/example-standard-toy-sexual-phylogeny.csv"
        ),
        pd.read_csv(
            f"{assets_path}/example-standard-toy-asexual-phylogeny.csv"
        ),
        pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
        pd.read_csv(f"{assets_path}/nk_tournamentselection.csv"),
        pd.read_csv(f"{assets_path}/nk_tournamentselection.csv")[-1:0],
        None,
    ],
)
@pytest.mark.parametrize(
    "apply",
    [
        alifestd_try_add_ancestor_id_col,
        alifestd_to_working_format,
        lambda x: x,
    ],
)
@pytest.mark.parametrize(
    "apply_all",
    [
        True,
        False,
    ],
)
def test_alifestd_aggregate_phylogenies(
    phylogeny_df1,
    phylogeny_df2,
    phylogeny_df3,
    apply,
    apply_all,
):

    if phylogeny_df3 is None and phylogeny_df2 is not None:
        return

    phylogeny_df1 = apply(phylogeny_df1)
    phylogeny_df1_ = phylogeny_df1.copy()
    phylogenies = [phylogeny_df1]
    if phylogeny_df2 is not None:
        if apply_all:
            phylogeny_df2 = apply(phylogeny_df2)
        phylogeny_df2_ = phylogeny_df2.copy()
        phylogenies.append(phylogeny_df2)
    if phylogeny_df3 is not None:
        if apply_all:
            phylogeny_df3 = apply(phylogeny_df3)
        phylogeny_df3_ = phylogeny_df3.copy()
        phylogenies.append(phylogeny_df3)

    aggregate_df = alifestd_aggregate_phylogenies(phylogenies)
    assert alifestd_validate(aggregate_df)
    # check for side effects
    assert phylogeny_df1.equals(phylogeny_df1_)
    if phylogeny_df2 is not None:
        assert phylogeny_df2.equals(phylogeny_df2_)
    if phylogeny_df3 is not None:
        assert phylogeny_df3.equals(phylogeny_df3_)

    assert len(alifestd_find_leaf_ids(aggregate_df)) == sum(
        map(len, map(alifestd_find_leaf_ids, phylogenies)),
    )
    assert all(
        map(alifestd_has_contiguous_ids, phylogenies)
    ) == alifestd_has_contiguous_ids(aggregate_df)
    assert all(map(alifestd_is_asexual, phylogenies)) == alifestd_is_asexual(
        aggregate_df
    )
    assert all(
        map(alifestd_is_topologically_sorted, phylogenies)
    ) == alifestd_is_topologically_sorted(aggregate_df)
    assert any(map(alifestd_is_sexual, phylogenies)) == alifestd_is_sexual(
        aggregate_df
    )

    assert len(aggregate_df["id"].unique()) == len(aggregate_df["id"])
    if "ancestor_id" in aggregate_df:
        assert (
            aggregate_df["ancestor_id"]
            == alifestd_make_ancestor_id_col(
                aggregate_df["id"], aggregate_df["ancestor_list"]
            )
        ).all()

    if alifestd_is_asexual(aggregate_df):
        assert len(apc.alife_dataframe_to_dendropy_trees(aggregate_df)) == sum(
            bool(len(phylogeny)) for phylogeny in phylogenies
        )
        assert Counter(
            (node.level(), len(node.child_nodes()))
            for tree in apc.alife_dataframe_to_dendropy_trees(aggregate_df)
            for node in tree
        ) == Counter(
            (node.level(), len(node.child_nodes()))
            for tree in map(apc.alife_dataframe_to_dendropy_tree, phylogenies)
            if tree is not None
            for node in tree
        )
