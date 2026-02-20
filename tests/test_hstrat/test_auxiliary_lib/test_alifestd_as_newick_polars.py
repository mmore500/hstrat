import os
import unittest.mock

import alifedata_phyloinformatics_convert as apc
import pandas as pd
import polars as pl
import pytest

from hstrat._auxiliary_lib import (
    alifestd_as_newick_asexual,
    alifestd_as_newick_polars,
    alifestd_try_add_ancestor_id_col,
)

assets_path = os.path.join(os.path.dirname(__file__), "assets")


def test_fuzz():
    phylogeny_df = pd.read_csv(
        f"{assets_path}/example-standard-toy-asexual-phylogeny.csv"
    )
    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df)
    phylogeny_pl = pl.from_pandas(phylogeny_df)

    result = alifestd_as_newick_polars(phylogeny_pl, taxon_label="id")

    rosetta_tree = apc.RosettaTree.from_newick(result)
    reconstructed = rosetta_tree.as_alife
    reconstructed["taxon_label"] = reconstructed["taxon_label"].fillna(
        reconstructed["label"],
    )
    reconstructed["taxon_label"] = reconstructed["taxon_label"].astype(int)
    reconstructed = alifestd_try_add_ancestor_id_col(reconstructed)

    assert len(reconstructed) == len(phylogeny_df)

    taxon_labels = dict(zip(reconstructed["id"], reconstructed["taxon_label"]))
    assert set(zip(phylogeny_df["id"], phylogeny_df["ancestor_id"])) == set(
        zip(
            reconstructed["taxon_label"],
            reconstructed["ancestor_id"].map(taxon_labels),
        )
    ), (phylogeny_df, result, rosetta_tree.as_newick)


def test_empty():
    phylogeny_pl = pl.DataFrame(
        {
            "id": pl.Series([], dtype=pl.Int64),
            "ancestor_list": pl.Series([], dtype=pl.Utf8),
        },
    )
    res = alifestd_as_newick_polars(phylogeny_pl)
    assert res == ";"


def test_simple1():
    phylogeny_df = pl.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_list": ["[None]", "[0]", "[1]"],
            "origin_time_delta": [3.1, 4.0, 1.0],
        },
    )
    result = alifestd_as_newick_polars(
        phylogeny_df,
        taxon_label=None,
    )
    assert result == "((:1):4):3.1;"


def test_simple2_non_contiguous():
    phylogeny_df = pl.DataFrame(
        {
            "id": [3, 0, 1, 2],
            "ancestor_list": ["[0]", "[1]", "[None]", "[1]"],
        },
    )
    with pytest.raises(NotImplementedError):
        alifestd_as_newick_polars(
            phylogeny_df,
            taxon_label=None,
        )


def test_simple3_non_contiguous():
    phylogeny_df = pl.DataFrame(
        {
            "id": [4, 0, 2, 3],
            "ancestor_list": ["[None]", "[None]", "[0]", "[4]"],
            "label": ["A", "B", "C", "D"],
        },
    )
    with pytest.raises(NotImplementedError):
        alifestd_as_newick_polars(
            phylogeny_df,
            taxon_label="label",
        )


def test_simple4():
    phylogeny_df = pl.DataFrame(
        {
            "id": [0, 1, 2, 3, 4],
            "ancestor_list": ["[None]", "[0]", "[0]", "[1]", "[0]"],
            "origin_time": [0, 1, 2, 5, 90],
        },
    )
    result = alifestd_as_newick_polars(
        phylogeny_df,
        taxon_label="id",
    )

    assert result == "(4:90,2:2,(3:4)1:1)0:0;"


def test_matches_pandas_contiguous():
    """Verify the polars wrapper produces the same output as the pandas
    implementation for datasets with contiguous IDs."""
    phylogeny_pd = pd.read_csv(
        f"{assets_path}/example-standard-toy-asexual-phylogeny.csv"
    )
    phylogeny_pd = alifestd_try_add_ancestor_id_col(phylogeny_pd)
    phylogeny_pl = pl.from_pandas(phylogeny_pd)

    result_pd = alifestd_as_newick_asexual(phylogeny_pd, taxon_label="id")
    result_pl = alifestd_as_newick_polars(
        phylogeny_pl, taxon_label="id"
    )

    assert result_pd == result_pl


def test_no_polars_to_pandas_conversion():
    """Verify that no polars-to-pandas conversion occurs internally."""
    phylogeny_df = pl.DataFrame(
        {
            "id": [0, 1, 2, 3, 4],
            "ancestor_list": ["[None]", "[0]", "[0]", "[1]", "[0]"],
            "origin_time": [0, 1, 2, 5, 90],
        },
    )

    with unittest.mock.patch(
        "polars.DataFrame.to_pandas",
        side_effect=AssertionError(
            "polars-to-pandas conversion should not occur"
        ),
    ):
        with unittest.mock.patch(
            "polars.Series.to_pandas",
            side_effect=AssertionError(
                "polars Series-to-pandas conversion should not occur"
            ),
        ):
            result = alifestd_as_newick_polars(
                phylogeny_df,
                taxon_label="id",
            )

    assert result == "(4:90,2:2,(3:4)1:1)0:0;"


def test_input_not_mutated():
    """Verify the input DataFrame is not modified."""
    phylogeny_df = pl.DataFrame(
        {
            "id": [0, 1, 2, 3, 4],
            "ancestor_list": ["[None]", "[0]", "[0]", "[1]", "[0]"],
            "origin_time": [0, 1, 2, 5, 90],
        },
    )
    original = phylogeny_df.clone()

    alifestd_as_newick_polars(
        phylogeny_df,
        taxon_label="id",
    )

    assert phylogeny_df.equals(original)


def test_with_ancestor_id_col():
    """Test with pre-existing ancestor_id column (no ancestor_list)."""
    phylogeny_df = pl.DataFrame(
        {
            "id": [0, 1, 2, 3, 4],
            "ancestor_id": [0, 0, 0, 1, 0],
            "origin_time": [0, 1, 2, 5, 90],
        },
    )
    result = alifestd_as_newick_polars(
        phylogeny_df,
        taxon_label="id",
    )
    assert result == "(4:90,2:2,(3:4)1:1)0:0;"


def test_non_contiguous_ids():
    """Test that non-contiguous IDs raise NotImplementedError."""
    phylogeny_df = pl.DataFrame(
        {
            "id": [10, 20, 30],
            "ancestor_id": [10, 10, 20],
            "origin_time_delta": [3.1, 4.0, 1.0],
        },
    )
    with pytest.raises(NotImplementedError):
        alifestd_as_newick_polars(
            phylogeny_df,
            taxon_label=None,
        )


def test_non_topologically_sorted():
    """Test that non-topologically-sorted data raises NotImplementedError."""
    phylogeny_df = pl.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_id": [1, 1, 0],
            "origin_time_delta": [1.0, 3.1, 4.0],
        },
    )
    with pytest.raises(NotImplementedError):
        alifestd_as_newick_polars(
            phylogeny_df,
            taxon_label=None,
        )


def test_lazyframe_input():
    """Test that LazyFrame input works correctly."""
    phylogeny_df = pl.DataFrame(
        {
            "id": [0, 1, 2, 3, 4],
            "ancestor_list": ["[None]", "[0]", "[0]", "[1]", "[0]"],
            "origin_time": [0, 1, 2, 5, 90],
        },
    )
    lazy_df = phylogeny_df.lazy()

    result = alifestd_as_newick_polars(
        lazy_df,
        taxon_label="id",
    )

    assert result == "(4:90,2:2,(3:4)1:1)0:0;"


def test_lazyframe_empty():
    """Test that empty LazyFrame returns ';'."""
    phylogeny_pl = pl.DataFrame(
        {
            "id": pl.Series([], dtype=pl.Int64),
            "ancestor_list": pl.Series([], dtype=pl.Utf8),
        },
    ).lazy()
    res = alifestd_as_newick_polars(phylogeny_pl)
    assert res == ";"
