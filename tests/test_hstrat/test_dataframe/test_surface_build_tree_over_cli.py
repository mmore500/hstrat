import os
import pathlib
import subprocess

from phyloframe import legacy as pfl
import polars as pl
import pytest

assets = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


@pytest.fixture(scope="module")
def genomes_file() -> str:
    output_file = "/tmp/hstrat_surface_build_tree_over_td.pqt"  # nosec B108
    pathlib.Path(output_file).unlink(missing_ok=True)
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat.dataframe.surface_test_drive",
            output_file,
        ],
        check=True,
        input=f"{assets}/nk_ecoeaselection.csv".encode(),
    )
    return output_file


def _run_cli(module: str, input_file: str, output_file: str, *args: str):
    pathlib.Path(output_file).unlink(missing_ok=True)
    subprocess.run(  # nosec B603
        ["python3", "-m", module, output_file, *args],
        check=True,
        input=input_file.encode(),
    )
    return pl.read_parquet(output_file)


def test_surface_build_tree_over_cli_help():
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat.dataframe.surface_build_tree_over",
            "--help",
        ],
        check=True,
    )


def test_surface_build_tree_over_cli_version():
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat.dataframe.surface_build_tree_over",
            "--version",
        ],
        check=True,
    )


def test_surface_build_tree_over_cli_requires_partition_by():
    result = subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat.dataframe.surface_build_tree_over",
            "/tmp/hstrat_surface_build_tree_over_noflag.pqt",  # nosec B108
        ],
        capture_output=True,
        input=f"{assets}/packed.csv".encode(),
    )
    assert result.returncode != 0
    assert b"--partition-by" in result.stderr


def test_surface_build_tree_over_cli_csv():
    output_file = "/tmp/hstrat_surface_build_tree_over.csv"  # nosec B108
    pathlib.Path(output_file).unlink(missing_ok=True)
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat.dataframe.surface_build_tree_over",
            output_file,
            "--partition-by",
            'awoo="awoo"',
        ],
        check=True,
        input=f"{assets}/packed.csv".encode(),
    )
    assert os.path.exists(output_file)


@pytest.mark.parametrize(
    "partition_by",
    [
        ['awoo="awoo"'],
        ['awoo=pl.col("awoo")'],
        ['awoo_len=pl.col("awoo").str.len_chars()', 'awoo="awoo"'],
    ],
)
def test_surface_build_tree_over_cli_partition_by(partition_by: list):
    res = _run_cli(
        "hstrat.dataframe.surface_build_tree_over",
        f"{assets}/packed.csv",
        "/tmp/hstrat_surface_build_tree_over_by.pqt",  # nosec B108
        *(arg for value in partition_by for arg in ("--partition-by", value)),
    )
    # one independent tree per partition
    assert pfl.alifestd_count_root_nodes_polars(res) == 2
    assert res["id"].is_unique().all()
    assert res["dstream_data_id"].drop_nulls().sort().to_list() == [0, 1]
    # partition keys forwarded to all rows, including inner nodes
    assert res["awoo"].null_count() == 0
    assert res["awoo"].unique(maintain_order=True).to_list() == ["bar", "baz"]
    # partitions are not connected
    for awoo in "bar", "baz":
        part = res.filter(pl.col("awoo") == awoo)
        assert set(part["ancestor_id"]) <= set(part["id"])


def test_surface_build_tree_over_cli_filepath():
    output_file = "/tmp/hstrat_surface_build_tree_over_fp.pqt"  # nosec B108
    pathlib.Path(output_file).unlink(missing_ok=True)
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat.dataframe.surface_build_tree_over",
            output_file,
            "--with-column",
            'pl.lit(filepath).alias("source")',
            "--how",
            "diagonal_relaxed",
            "--partition-by",
            'source="source"',
        ],
        check=True,
        input=f"{assets}/packed.csv\n{assets}/packed_long.csv".encode(),
    )
    res = pl.read_parquet(output_file)
    assert res["source"].n_unique() == 2
    assert res["source"].null_count() == 0
    # dstream_data_id assigned before partitioning, so unique across files
    assert res["dstream_data_id"].drop_nulls().is_unique().all()
    assert res["dstream_data_id"].drop_nulls().len() == 4


def test_surface_build_tree_over_cli_matches_separate(genomes_file: str):
    key = 'pl.col("td_source_id") % 3'
    res = _run_cli(
        "hstrat.dataframe.surface_build_tree_over",
        genomes_file,
        "/tmp/hstrat_surface_build_tree_over_cmp.pqt",  # nosec B108
        "--partition-by",
        f"part={key}",
    )
    assert res["id"].is_unique().all()
    assert res["part"].null_count() == 0
    assert res["part"].unique(maintain_order=True).to_list() == [
        *pl.read_parquet(genomes_file)
        .select(pl.col("td_source_id") % 3)
        .to_series()
        .unique(maintain_order=True)
    ]

    for part in range(3):
        expected = _run_cli(
            "hstrat.dataframe.surface_build_tree",
            genomes_file,
            "/tmp/hstrat_surface_build_tree_over_ref.pqt",  # nosec B108
            "--filter",
            f"{key} == {part}",
        )
        actual = res.filter(pl.col("part") == part).drop("part")

        assert len(actual) == len(expected)
        assert set(actual["ancestor_id"]) <= set(actual["id"])
        assert pfl.alifestd_test_leaves_isomorphic_asexual(
            pfl.alifestd_assign_contiguous_ids(actual.to_pandas()),
            expected.to_pandas(),
            taxon_label="td_source_id",
        )


def test_surface_build_tree_over_cli_empty():
    res = _run_cli(
        "hstrat.dataframe.surface_build_tree_over",
        f"{assets}/packed.csv",
        "/tmp/hstrat_surface_build_tree_over_empty.pqt",  # nosec B108
        "--filter",
        "False",
        "--partition-by",
        'awoo="awoo"',
    )
    assert res.is_empty()
    assert {"id", "ancestor_id"} <= {*res.columns}
