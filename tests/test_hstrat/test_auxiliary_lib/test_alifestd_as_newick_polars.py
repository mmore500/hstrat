import os
import typing

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


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_fuzz(apply: typing.Callable):
    phylogeny_df = pd.read_csv(
        f"{assets_path}/example-standard-toy-asexual-phylogeny.csv"
    )
    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df)
    phylogeny_pl = apply(pl.from_pandas(phylogeny_df))

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


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_empty(apply: typing.Callable):
    phylogeny_pl = apply(
        pl.DataFrame(
            {
                "id": pl.Series([], dtype=pl.Int64),
                "ancestor_list": pl.Series([], dtype=pl.Utf8),
            },
        )
    )
    res = alifestd_as_newick_polars(phylogeny_pl)
    assert res == ";"


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_simple1(apply: typing.Callable):
    phylogeny_df = apply(
        pl.DataFrame(
            {
                "id": [0, 1, 2],
                "ancestor_list": ["[None]", "[0]", "[1]"],
                "origin_time_delta": [3.1, 4.0, 1.0],
            },
        )
    )
    result = alifestd_as_newick_polars(
        phylogeny_df,
        taxon_label=None,
    )
    assert result == "((:1):4):3.1;"


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_simple2_non_contiguous(apply: typing.Callable):
    phylogeny_df = apply(
        pl.DataFrame(
            {
                "id": [3, 0, 1, 2],
                "ancestor_list": ["[0]", "[1]", "[None]", "[1]"],
            },
        )
    )
    with pytest.raises(NotImplementedError):
        alifestd_as_newick_polars(
            phylogeny_df,
            taxon_label=None,
        )


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_simple3_non_contiguous(apply: typing.Callable):
    phylogeny_df = apply(
        pl.DataFrame(
            {
                "id": [4, 0, 2, 3],
                "ancestor_list": ["[None]", "[None]", "[0]", "[4]"],
                "label": ["A", "B", "C", "D"],
            },
        )
    )
    with pytest.raises(NotImplementedError):
        alifestd_as_newick_polars(
            phylogeny_df,
            taxon_label="label",
        )


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_simple4(apply: typing.Callable):
    phylogeny_df = apply(
        pl.DataFrame(
            {
                "id": [0, 1, 2, 3, 4],
                "ancestor_list": ["[None]", "[0]", "[0]", "[1]", "[0]"],
                "origin_time": [0, 1, 2, 5, 90],
            },
        )
    )
    result = alifestd_as_newick_polars(
        phylogeny_df,
        taxon_label="id",
    )

    assert result == "(4:90,2:2,(3:4)1:1)0:0;"


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_matches_pandas_contiguous(apply: typing.Callable):
    """Verify the polars wrapper produces the same output as the pandas
    implementation for datasets with contiguous IDs."""
    phylogeny_pd = pd.read_csv(
        f"{assets_path}/example-standard-toy-asexual-phylogeny.csv"
    )
    phylogeny_pd = alifestd_try_add_ancestor_id_col(phylogeny_pd)
    phylogeny_pl = apply(pl.from_pandas(phylogeny_pd))

    result_pd = alifestd_as_newick_asexual(phylogeny_pd, taxon_label="id")
    result_pl = alifestd_as_newick_polars(phylogeny_pl, taxon_label="id")

    assert result_pd == result_pl


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_input_not_mutated(apply: typing.Callable):
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
        apply(phylogeny_df),
        taxon_label="id",
    )

    assert phylogeny_df.equals(original)


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_with_ancestor_id_col(apply: typing.Callable):
    """Test with pre-existing ancestor_id column (no ancestor_list)."""
    phylogeny_df = apply(
        pl.DataFrame(
            {
                "id": [0, 1, 2, 3, 4],
                "ancestor_id": [0, 0, 0, 1, 0],
                "origin_time": [0, 1, 2, 5, 90],
            },
        )
    )
    result = alifestd_as_newick_polars(
        phylogeny_df,
        taxon_label="id",
    )
    assert result == "(4:90,2:2,(3:4)1:1)0:0;"


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_non_contiguous_ids(apply: typing.Callable):
    """Test that non-contiguous IDs raise NotImplementedError."""
    phylogeny_df = apply(
        pl.DataFrame(
            {
                "id": [10, 20, 30],
                "ancestor_id": [10, 10, 20],
                "origin_time_delta": [3.1, 4.0, 1.0],
            },
        )
    )
    with pytest.raises(NotImplementedError):
        alifestd_as_newick_polars(
            phylogeny_df,
            taxon_label=None,
        )


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_non_topologically_sorted(apply: typing.Callable):
    """Test that non-topologically-sorted data raises NotImplementedError."""
    phylogeny_df = apply(
        pl.DataFrame(
            {
                "id": [0, 1, 2],
                "ancestor_id": [1, 1, 0],
                "origin_time_delta": [1.0, 3.1, 4.0],
            },
        )
    )
    with pytest.raises(NotImplementedError):
        alifestd_as_newick_polars(
            phylogeny_df,
            taxon_label=None,
        )
