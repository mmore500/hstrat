import os

import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_aggregate_phylogenies,
    alifestd_collapse_unifurcations,
    alifestd_make_empty,
    alifestd_test_leaves_isomorphic_asexual,
)

assets_path = os.path.join(os.path.dirname(__file__), "assets")


def test_empty():
    mt = alifestd_make_empty()
    mt["taxon_label"] = None
    assert alifestd_test_leaves_isomorphic_asexual(mt, mt, "taxon_label")


def test_mutate():
    original_df = pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv")
    original_df["taxon_label"] = original_df["id"]
    df = original_df.copy()
    alifestd_test_leaves_isomorphic_asexual(
        df, df, "taxon_label", mutate=False
    )
    assert df.equals(original_df)


@pytest.mark.parametrize(
    "phylogeny_df",
    [
        pd.read_csv(
            f"{assets_path}/example-standard-toy-asexual-phylogeny.csv"
        ),
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
def test_fuzz_positive1(phylogeny_df: pd.DataFrame):

    phylogeny_df["taxon_label"] = phylogeny_df["id"]
    assert alifestd_test_leaves_isomorphic_asexual(
        phylogeny_df, phylogeny_df, "taxon_label"
    )
    assert alifestd_test_leaves_isomorphic_asexual(
        phylogeny_df,
        alifestd_collapse_unifurcations(phylogeny_df),
        "taxon_label",
    )
    assert alifestd_test_leaves_isomorphic_asexual(
        phylogeny_df,
        phylogeny_df.sample(frac=1).reset_index(drop=True),
        "taxon_label",
    )


@pytest.mark.parametrize(
    "phylogeny_df",
    [
        pd.read_csv(
            f"{assets_path}/example-standard-toy-asexual-phylogeny.csv"
        ),
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
def test_fuzz_positive2(phylogeny_df: pd.DataFrame):

    phylogeny_df["taxon_label"] = phylogeny_df["id"].astype(str)
    assert alifestd_test_leaves_isomorphic_asexual(
        phylogeny_df, phylogeny_df, "taxon_label"
    )
    assert alifestd_test_leaves_isomorphic_asexual(
        phylogeny_df,
        alifestd_collapse_unifurcations(phylogeny_df),
        "taxon_label",
    )
    assert alifestd_test_leaves_isomorphic_asexual(
        phylogeny_df,
        phylogeny_df.sample(frac=1).reset_index(drop=True),
        "taxon_label",
    )


def test_negative1():
    df1 = pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv")
    df2 = pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv")
    df1["taxon_label"] = df1["id"]
    df2["taxon_label"] = df2["id"]
    assert not alifestd_test_leaves_isomorphic_asexual(df1, df2, "taxon_label")


def test_negative2():
    df1 = pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv")
    df2 = pd.read_csv(f"{assets_path}/nk_ecoeaselection_tweaked.csv")
    df1["taxon_label"] = df1["id"].astype(str)
    df2["taxon_label"] = df2["id"].astype(str)
    assert not alifestd_test_leaves_isomorphic_asexual(df1, df2, "taxon_label")
