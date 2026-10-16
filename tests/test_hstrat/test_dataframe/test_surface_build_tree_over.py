import os

from phyloframe import legacy as pfl
import polars as pl
import pytest

from hstrat.dataframe import surface_build_tree, surface_build_tree_over

assets_path = os.path.join(os.path.dirname(__file__), "assets")


@pytest.mark.parametrize(
    "partition_by",
    [
        "awoo",
        pl.col("awoo"),
        ["awoo"],
        [pl.col("awoo").str.len_chars().alias("awoo_len"), "awoo"],
    ],
)
def test_partition_by(partition_by):
    df = pl.read_csv(f"{assets_path}/packed.csv")
    res = surface_build_tree_over(df, partition_by=partition_by)

    # one independent tree per partition
    assert pfl.alifestd_count_root_nodes_polars(res) == 2
    assert res["id"].is_unique().all()
    assert res["dstream_data_id"].drop_nulls().len() == 2
    # partition keys forwarded to all rows, including inner nodes
    assert res["awoo"].null_count() == 0
    assert res["awoo"].unique(maintain_order=True).to_list() == ["bar", "baz"]
    # partitions are not connected
    for awoo in "bar", "baz":
        part = res.filter(pl.col("awoo") == awoo)
        assert set(part["ancestor_id"]) <= set(part["id"])


def test_lazyframe():
    df = pl.read_csv(f"{assets_path}/packed.csv")
    res = surface_build_tree_over(df.lazy(), partition_by="awoo")
    assert res.equals(surface_build_tree_over(df, partition_by="awoo"))


def test_single_partition_matches_surface_build_tree():
    df = pl.read_csv(f"{assets_path}/packed.csv")
    res = surface_build_tree_over(
        df,
        partition_by=pl.lit("x").alias("partition"),
        collapse_unif_freq=0,
    )
    expected = surface_build_tree(df, collapse_unif_freq=0)
    assert res.drop("partition").equals(expected)
    assert res["partition"].to_list() == ["x"] * len(res)


def test_progress_wrap():
    df = pl.read_csv(f"{assets_path}/packed.csv")
    calls = []

    def progress_wrap(iterable):
        calls.append(iterable)
        return iterable

    surface_build_tree_over(
        df, partition_by="awoo", progress_wrap=progress_wrap
    )
    assert len(calls) == 1


def test_empty():
    df = pl.read_csv(f"{assets_path}/packed.csv").head(0)
    res = surface_build_tree_over(df, partition_by="awoo")
    assert res.is_empty()
    assert {"id", "ancestor_id"} <= {*res.columns}
